from __future__ import annotations

import csv
import argparse
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


REPO_ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = Path(__file__).resolve().with_name("bn_Hisnul_Elmuslim.pdf")
SUNNAH_CSV_PATH = REPO_ROOT / "python_scripts" / "hisnul_muslim_scrapper" / "sunnah_duas.csv"
OUTPUT_CSV_PATH = Path(__file__).resolve().with_name("bn_hisnul_duas.csv")
REVIEW_CSV_PATH = Path(__file__).resolve().with_name("bn_hisnul_duas_review.csv")

PAGE_START = 23

ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
BENGALI_RE = re.compile(r"[\u0980-\u09FF]")
DIGIT_START_RE = re.compile(r"^[0-9০-৯]+(?:\s*[-.)]|\s*[-–—]\s*)")
REF_START_RE = re.compile(r"^[0-9০-৯]+\s*$")
SPACE_RE = re.compile(r"\s+")

HEADER_NOISE = {
    "দদা‘আ ও যিযকরসমূ হ",
    "দো'আ ও যিকিরসমূহ",
    "force",
}


@dataclass
class PageEntry:
    dua_id: str
    pdf_seq: int
    pdf_page: int
    arabic_pdf: str
    transliteration_bn: str
    bengali_translation: str
    reference_bn: str
    parse_flags: str


def run_command(args: List[str], *, input_bytes: bytes | None = None) -> str:
    completed = subprocess.run(
        args,
        input=input_bytes,
        capture_output=True,
        check=True,
    )
    return completed.stdout.decode("utf-8", errors="ignore")


def normalize_text(text: str) -> str:
    return SPACE_RE.sub(" ", text).strip()


def bengali_ratio(text: str) -> float:
    if not text:
        return 0.0
    return len(BENGALI_RE.findall(text)) / max(len(text), 1)


def is_probably_bengali(text: str) -> bool:
    return bengali_ratio(text) > 0.15


def is_translit_start(line: str) -> bool:
    return line.startswith("(") and is_probably_bengali(line)


def is_header_noise(line: str) -> bool:
    line = normalize_text(line)
    if not line:
        return True
    if line in HEADER_NOISE:
        return True
    if "" in line or "" in line:
        return True
    if line.startswith("পৃষ্ঠা") or line.startswith("Page "):
        return True
    if line.startswith("দো'আ ও যিকিরসমূহ"):
        return True
    return False


def clean_ocr_lines(text: str) -> List[str]:
    lines = []
    for raw_line in text.splitlines():
        line = normalize_text(raw_line.replace(">", "").replace("_", ""))
        if not line:
            continue
        if is_header_noise(line):
            continue
        lines.append(line)
    return lines


def clean_text_layer_lines(text: str) -> List[str]:
    lines = []
    for raw_line in text.splitlines():
        line = normalize_text(raw_line)
        if not line:
            continue
        if is_header_noise(line):
            continue
        lines.append(line)
    return lines


def extract_pdf_page_count(pdf_path: Path) -> int:
    info = run_command(["pdfinfo", str(pdf_path)])
    for line in info.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError("Could not determine PDF page count.")


def render_pages(pdf_path: Path, output_dir: Path, page_start: int, page_end: int) -> List[Path]:
    prefix = output_dir / "page"
    subprocess.run(
        [
            "pdftocairo",
            "-f",
            str(page_start),
            "-l",
            str(page_end),
            "-png",
            str(pdf_path),
            str(prefix),
        ],
        check=True,
        capture_output=True,
    )
    page_paths = sorted(output_dir.glob("page-*.png"))
    if not page_paths:
        raise RuntimeError("Page rendering failed; no PNG files were produced.")
    return page_paths


def ocr_page(image_path: Path) -> str:
    return run_command(
        ["tesseract", "stdin", "stdout", "-l", "ben+ara+eng", "--psm", "6"],
        input_bytes=image_path.read_bytes(),
    )


def extract_text_layer_page(pdf_path: Path, page_num: int) -> str:
    return run_command(
        [
            "pdftotext",
            "-f",
            str(page_num),
            "-l",
            str(page_num),
            "-layout",
            str(pdf_path),
            "-",
        ]
    )


def extract_arabic_blocks(lines: Iterable[str]) -> List[str]:
    blocks: List[List[str]] = []
    current: List[str] = []

    for line in lines:
        if ARABIC_RE.search(line):
            current.append(line)
            continue
        if current:
            blocks.append(current)
            current = []

    if current:
        blocks.append(current)

    cleaned_blocks = []
    for block in blocks:
        text = normalize_text(" ".join(block))
        text = re.sub(r"^[0-9০-৯]+(?:\s*[-.)]|\s*\(-\s*[0-9০-৯]+\))?\s*", "", text)
        cleaned_blocks.append(text)

    return [block for block in cleaned_blocks if block]


def extract_reference_blocks(lines: List[str]) -> List[str]:
    blocks: List[List[str]] = []
    current: List[str] = []
    in_refs = False

    for line in lines:
        if REF_START_RE.match(line):
            if current:
                blocks.append(current)
            current = [line]
            in_refs = True
            continue

        if in_refs:
            if ARABIC_RE.search(line):
                continue
            if DIGIT_START_RE.match(line) and current:
                blocks.append(current)
                current = [line]
                continue
            current.append(line)

    if current:
        blocks.append(current)

    refs = []
    for block in blocks:
        text = normalize_text(" ".join(block))
        if any(keyword in text for keyword in ["বুখ", "মুসল", "তিরমি", "নাসা", "ইবন", "আবূ", "আহম", "দার", "বারী"]):
            refs.append(text)
    return refs


def parse_ocr_entries(lines: List[str]) -> List[dict[str, str]]:
    entries: List[dict[str, str]] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if not is_translit_start(line):
            i += 1
            continue

        translit_lines = [line]
        i += 1
        while i < len(lines):
            next_line = lines[i]
            if is_translit_start(next_line):
                break
            if DIGIT_START_RE.match(next_line):
                break
            if next_line.endswith(")") and is_probably_bengali(next_line):
                translit_lines.append(next_line)
                i += 1
                break
            if is_probably_bengali(next_line):
                translit_lines.append(next_line)
                i += 1
                if next_line.endswith(")"):
                    break
                continue
            break

        translation_lines: List[str] = []
        while i < len(lines):
            next_line = lines[i]
            if is_translit_start(next_line):
                break
            if REF_START_RE.match(next_line):
                break
            if not is_probably_bengali(next_line):
                i += 1
                continue
            translation_lines.append(next_line)
            i += 1
            if translation_lines and translation_lines[-1].endswith("।"):
                # Most translation blocks finish before references or the next transliteration.
                if i < len(lines) and (
                    is_translit_start(lines[i]) or REF_START_RE.match(lines[i])
                ):
                    break

        translit_text = normalize_text(" ".join(translit_lines))
        translit_text = translit_text.strip()
        if translit_text.startswith("("):
            translit_text = translit_text[1:]
        if translit_text.endswith(")"):
            translit_text = translit_text[:-1]
        translit_text = normalize_text(translit_text)

        translation_text = normalize_text(" ".join(translation_lines))
        translation_text = re.sub(r"^[0-9০-৯]+(?:\s*[-.)]|\s*[-–—]\s*)", "", translation_text)
        translation_text = normalize_text(translation_text)

        entries.append(
            {
                "transliteration_bn": translit_text,
                "bengali_translation": translation_text,
            }
        )

    return [entry for entry in entries if entry["transliteration_bn"] or entry["bengali_translation"]]


def load_sunnah_rows(csv_path: Path) -> List[dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_dataset(page_start: int = PAGE_START, page_end: int | None = None) -> tuple[List[PageEntry], List[dict[str, str]]]:
    if page_end is None:
        page_end = extract_pdf_page_count(PDF_PATH)
    sunnah_rows = load_sunnah_rows(SUNNAH_CSV_PATH)

    entries: List[PageEntry] = []
    review_rows: List[dict[str, str]] = []
    pdf_seq = 1

    with tempfile.TemporaryDirectory(prefix="bn_hisnul_pdf_") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        page_images = render_pages(PDF_PATH, temp_dir, page_start, page_end)

        for image_path in page_images:
            page_num = int(image_path.stem.split("-")[-1])
            ocr_lines = clean_ocr_lines(ocr_page(image_path))
            text_layer_lines = clean_text_layer_lines(extract_text_layer_page(PDF_PATH, page_num))

            ocr_entries = parse_ocr_entries(ocr_lines)
            arabic_blocks = extract_arabic_blocks(text_layer_lines)
            reference_blocks = extract_reference_blocks(text_layer_lines)

            entry_count = max(len(ocr_entries), len(arabic_blocks))
            flags = []
            if len(ocr_entries) != len(arabic_blocks):
                flags.append("entry_arabic_count_mismatch")
            if reference_blocks and len(reference_blocks) not in {0, entry_count}:
                flags.append("reference_count_mismatch")

            for idx in range(entry_count):
                arabic_text = arabic_blocks[idx] if idx < len(arabic_blocks) else ""
                translit_text = ocr_entries[idx]["transliteration_bn"] if idx < len(ocr_entries) else ""
                translation_text = ocr_entries[idx]["bengali_translation"] if idx < len(ocr_entries) else ""
                reference_text = reference_blocks[idx] if idx < len(reference_blocks) else ""
                parse_flags = ",".join(flags) if flags else ""

                entries.append(
                    PageEntry(
                        dua_id="",
                        pdf_seq=pdf_seq,
                        pdf_page=page_num,
                        arabic_pdf=arabic_text,
                        transliteration_bn=translit_text,
                        bengali_translation=translation_text,
                        reference_bn=reference_text,
                        parse_flags=parse_flags,
                    )
                )
                pdf_seq += 1

            review_rows.append(
                {
                    "pdf_page": str(page_num),
                    "ocr_entry_count": str(len(ocr_entries)),
                    "arabic_block_count": str(len(arabic_blocks)),
                    "reference_block_count": str(len(reference_blocks)),
                    "flags": ",".join(flags),
                }
            )

    if len(entries) != len(sunnah_rows):
        print(
            f"Warning: extracted {len(entries)} PDF entries but Sunnah has {len(sunnah_rows)} rows. "
            "The CSV will still be produced, but the mapping needs review."
        )

    for idx, entry in enumerate(entries):
        if idx < len(sunnah_rows):
            entry.dua_id = sunnah_rows[idx]["dua_id"]
        else:
            entry.dua_id = ""

    return entries, review_rows


def write_outputs(entries: List[PageEntry], review_rows: List[dict[str, str]]) -> None:
    output_fields = [
        "dua_id",
        "pdf_seq",
        "pdf_page",
        "arabic_pdf",
        "transliteration_bn",
        "bengali_translation",
        "reference_bn",
        "parse_flags",
    ]
    with OUTPUT_CSV_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        for entry in entries:
            writer.writerow(
                {
                    "dua_id": entry.dua_id,
                    "pdf_seq": entry.pdf_seq,
                    "pdf_page": entry.pdf_page,
                    "arabic_pdf": entry.arabic_pdf,
                    "transliteration_bn": entry.transliteration_bn,
                    "bengali_translation": entry.bengali_translation,
                    "reference_bn": entry.reference_bn,
                    "parse_flags": entry.parse_flags,
                }
            )

    with REVIEW_CSV_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        if review_rows:
            writer = csv.DictWriter(f, fieldnames=list(review_rows[0].keys()))
            writer.writeheader()
            writer.writerows(review_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract Bengali Hisnul Muslim PDF into a CSV dataset.")
    parser.add_argument("--page-start", type=int, default=PAGE_START)
    parser.add_argument("--page-end", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    entries, review_rows = build_dataset(page_start=args.page_start, page_end=args.page_end)
    write_outputs(entries, review_rows)
    print(f"Wrote {len(entries)} rows to {OUTPUT_CSV_PATH}")
    print(f"Wrote page review summary to {REVIEW_CSV_PATH}")


if __name__ == "__main__":
    main()
