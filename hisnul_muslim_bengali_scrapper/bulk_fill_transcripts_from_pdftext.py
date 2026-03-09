from __future__ import annotations

import argparse
import json
import subprocess
import unicodedata
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PDF_PATH = SCRIPT_DIR / "bn_Hisnul_Elmuslim.pdf"
TRANSCRIPT_DIR = SCRIPT_DIR / "page_transcripts_manual"
MANIFEST_PATH = TRANSCRIPT_DIR / "manifest.jsonl"

PAGE_HEADER_MARKERS = ("", "")
FOOTER_MARKERS = ("IslamHouse", "ISLAMHOUSE", "IslamHouse.com", "IsIAMHOUSE")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Populate page transcript files from the PDF text layer or OCR."
    )
    parser.add_argument("--page-start", type=int, default=39)
    parser.add_argument("--page-end", type=int, default=307)
    parser.add_argument("--source", choices=("pdf", "ocr"), default="pdf")
    parser.add_argument("--overwrite-existing", action="store_true")
    return parser.parse_args()


def extract_page_text(page_num: int) -> str:
    completed = subprocess.run(
        [
            "pdftotext",
            "-f",
            str(page_num),
            "-l",
            str(page_num),
            "-layout",
            str(PDF_PATH),
            "-",
        ],
        check=True,
        capture_output=True,
    )
    return completed.stdout.decode("utf-8", errors="ignore")


def extract_ocr_text(page_num: int) -> str:
    image_path = SCRIPT_DIR / "rendered_pages" / f"page_{page_num:03d}.png"
    completed = subprocess.run(
        [
            "tesseract",
            str(image_path),
            "stdout",
            "-l",
            "ben+ara+eng",
            "--psm",
            "4",
        ],
        check=True,
        capture_output=True,
    )
    return completed.stdout.decode("utf-8", errors="ignore")


def count_letter_chars_in_ranges(text: str, ranges: list[tuple[int, int]]) -> int:
    total = 0
    for char in text:
        code = ord(char)
        if any(start <= code <= end for start, end in ranges) and unicodedata.category(char).startswith("L"):
            total += 1
    return total


def is_garbage_ocr_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    bengali_count = count_letter_chars_in_ranges(stripped, [(0x0980, 0x09FF)])
    arabic_count = count_letter_chars_in_ranges(stripped, [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF)])
    latin_count = sum(char.isascii() and char.isalpha() for char in stripped)
    digit_count = sum(char.isdigit() for char in stripped)
    letter_like = bengali_count + arabic_count + latin_count
    visible_chars = sum(not char.isspace() for char in stripped)
    suspicious_ascii = sum(char.isascii() and not char.isalnum() and not char.isspace() for char in stripped)

    if bengali_count + arabic_count >= 3:
        return False
    if bengali_count >= 1 and len(stripped) > 6:
        if digit_count >= 3 or latin_count >= 3:
            return True
        return False
    if visible_chars > 0 and all(char in "()[]{}.,;:|/-_`'\"৳০১২৩৪৫৬৭৮৯0123456789" or char.isspace() for char in stripped):
        return True
    if letter_like == 0 and digit_count > 0:
        return True
    if digit_count >= 4 and bengali_count + arabic_count <= 1:
        return True
    if latin_count >= 4 and bengali_count + arabic_count == 0:
        return True
    if suspicious_ascii >= 3 and bengali_count + arabic_count <= 2:
        return True
    return False


def clean_page_text(raw_text: str) -> str:
    lines = raw_text.splitlines()
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append("")
            continue
        if PAGE_HEADER_MARKERS[0] in stripped and PAGE_HEADER_MARKERS[1] in stripped:
            continue
        if stripped in PAGE_HEADER_MARKERS:
            continue
        if stripped.isdigit():
            continue
        if stripped.startswith("") or stripped.startswith(""):
            continue
        if any(marker in stripped for marker in FOOTER_MARKERS):
            continue
        if stripped == "\f":
            continue
        cleaned.append(stripped)

    while cleaned and not cleaned[0]:
        cleaned.pop(0)
    while cleaned and not cleaned[-1]:
        cleaned.pop()

    normalized: list[str] = []
    previous_blank = False
    for line in cleaned:
        is_blank = line == ""
        if is_blank and previous_blank:
            continue
        normalized.append(line)
        previous_blank = is_blank
    text = "\n".join(normalized).strip()
    if not text:
        return "[[blank page]]"
    return text


def clean_ocr_text(raw_text: str) -> str:
    lines = raw_text.splitlines()
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append("")
            continue
        if any(marker in stripped for marker in FOOTER_MARKERS):
            continue
        if stripped in PAGE_HEADER_MARKERS:
            continue
        if stripped.startswith("(") and stripped.endswith(")") and len(stripped) <= 8:
            continue
        if is_garbage_ocr_line(stripped):
            continue
        cleaned.append(stripped)

    while cleaned and not cleaned[0]:
        cleaned.pop(0)
    while cleaned and not cleaned[-1]:
        cleaned.pop()

    normalized: list[str] = []
    previous_blank = False
    for line in cleaned:
        is_blank = line == ""
        if is_blank and previous_blank:
            continue
        normalized.append(line)
        previous_blank = is_blank

    text = "\n".join(normalized).strip()
    if not text:
        return "[[blank page]]"
    return text


def load_manifest() -> list[dict]:
    return [
        json.loads(line)
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def save_manifest(rows: list[dict]) -> None:
    with MANIFEST_PATH.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_header_only(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[:2]) + "\n\n"


def main() -> None:
    args = parse_args()
    rows = load_manifest()
    row_by_page = {int(row["page_num"]): row for row in rows}

    for page_num in range(args.page_start, args.page_end + 1):
        row = row_by_page.get(page_num)
        if row is None:
            continue
        transcript_path = TRANSCRIPT_DIR / row["transcript_file"]
        if not transcript_path.exists():
            raise FileNotFoundError(f"Missing transcript file: {transcript_path}")
        if row["status"] != "pending" and not args.overwrite_existing:
            continue

        header = read_header_only(transcript_path)
        if args.source == "ocr":
            body = clean_ocr_text(extract_ocr_text(page_num))
            note = "Bulk-filled from OCR; needs review."
        else:
            body = clean_page_text(extract_page_text(page_num))
            note = "Bulk-filled from PDF text layer; needs review."
        transcript_path.write_text(header + body + "\n", encoding="utf-8")

        row["status"] = "draft"
        row["notes"] = note
        print(f"Processed page {page_num} from {args.source}")

    save_manifest(rows)


if __name__ == "__main__":
    main()
