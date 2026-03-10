from __future__ import annotations

import argparse
import csv
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
TRANSCRIPT_DIR = SCRIPT_DIR / "page_transcripts_manual"
PDF_PATH = SCRIPT_DIR / "bn_Hisnul_Elmuslim.pdf"
OUTPUT_CSV = SCRIPT_DIR / "bn_hisnul_dua_dataset.csv"
REVIEW_CSV = SCRIPT_DIR / "bn_hisnul_dua_dataset_review.csv"

PAGE_START = 23
PAGE_END = 307

ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
BENGALI_RE = re.compile(r"[\u0980-\u09FF]")
SECTION_RE = re.compile(r"^([০-৯0-9]+)\.\s+(.+)$")
ENTRY_RE = re.compile(r"^([০-৯0-9]+(?:-\([০-৯0-9]+\)|-\([0-9]+\)|-[০-৯0-9]+)?)\s*(.*)$")
SUBENTRY_RE = re.compile(r"^\(([০-৯0-9]+)\)\s*(.*)$")
TRAILING_FOOTNOTE_RE = re.compile(r"([”\"'\]])?([০-৯0-9]{1,4})\.?$")
FOOTNOTE_MARKER_RE = re.compile(r"(?<=[”\"'’\]\)।.])([০-৯0-9]{1,4})(?=(?:[।.]|\s|$))")
QUOTE_LEAD_RE = re.compile(r"^[০-৯0-9]+(?:-\([০-৯0-9]+\)|-\([0-9]+\)|-[০-৯0-9]+)\s*[—-]?\s*")
INLINE_TRANSLIT_RE = re.compile(r"\(([^()]*[অ-হ][^()]*)\)")
SPACE_RE = re.compile(r"\s+")
CONTROL_RE = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]")
REFERENCE_KEYWORDS = (
    "বুখারী",
    "মুসলিম",
    "তিরমিযী",
    "আবু দাউদ",
    "আবূ দাউদ",
    "ইবন মাজাহ",
    "নাসাঈ",
    "আহমাদ",
    "হাকেম",
    "বায়হাকী",
    "মালেক",
    "ফাতহুল বারী",
)
TRANSLIT_END_RE = re.compile(r"\)[।.]?$")
END_MATTER_PREFIXES = (
    "وَصَلَّى اللَّهُ",
    "আল্লাহ দুরূদ ও সালাম",
    "এ বইটি",
    "`الذكر والدعاء",
)
MANUAL_REFERENCE_OVERRIDES = {
    "৩-(৩)": "তিরমিযী ৫/৪৭৩, নং ৩৪০১। দেখুন, সহীহুত তিরমিযী, ৩/১৪৪।",
}


@dataclass
class CandidateEntry:
    dua_seq: int
    section_title_bn: str
    entry_number_bn: str
    page_start: int
    page_end: int
    raw_lines: list[str] = field(default_factory=list)
    raw_pages: list[int] = field(default_factory=list)


@dataclass
class DuaRow:
    dua_seq: int
    section_title_bn: str
    page_start: int
    page_end: int
    entry_number_bn: str
    arabic: str
    transliteration_bn: str
    translation_bn: str
    reference_bn: str
    notes: str
    raw_pages: str
    parse_status: str
    review_flag: str
    source_excerpt: str


def normalize_text(text: str) -> str:
    text = CONTROL_RE.sub("", text)
    return SPACE_RE.sub(" ", text).strip()


def strip_headers(lines: list[str]) -> list[str]:
    if len(lines) >= 2 and lines[0].startswith("PAGE: ") and lines[1].startswith("SOURCE_IMAGE: "):
        lines = lines[2:]
    return lines


def bengali_digits_to_int(text: str) -> int | None:
    if not text:
        return None
    western = normalize_digits(text)
    return int(western) if western.isdigit() else None


def normalize_digits(text: str) -> str:
    trans = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
    return CONTROL_RE.sub("", text).translate(trans)


def clean_translation_line(line: str) -> str:
    line = QUOTE_LEAD_RE.sub("", line).strip()
    line = FOOTNOTE_MARKER_RE.sub("", line)
    line = line.rstrip(" .")
    return normalize_text(line)


def normalize_translation_text(text: str) -> str:
    match = re.match(r"^(\[[^\]]+\])\s+(.*)$", text)
    if match and match.group(1) in match.group(2):
        return normalize_text(match.group(2))
    return normalize_text(text)


def marks_translation_start(text: str) -> bool:
    text = normalize_text(text)
    if not text:
        return False
    return text.startswith(("“", "\"", "‘"))


def extract_inline_translit(line: str) -> tuple[str, str]:
    match = INLINE_TRANSLIT_RE.search(line)
    if not match:
        return "", line
    candidate = normalize_text(match.group(1))
    if not candidate or re.fullmatch(r"[০-৯0-9\s]+", candidate):
        return "", line
    if not any(marker in candidate for marker in ("-", "‘", "'", "’")):
        return "", line
    stripped = normalize_text(f"{line[:match.start()]} {line[match.end():]}")
    return candidate, stripped


def entry_base_number(marker: str) -> str:
    return normalize_digits(marker.split("-", 1)[0])


def is_reference_line(line: str) -> bool:
    line = normalize_text(line)
    return any(keyword in line for keyword in REFERENCE_KEYWORDS)


def looks_like_translit(line: str) -> bool:
    line = line.strip()
    if re.match(r"^\([০-৯0-9]+\)", line):
        return False
    return line.startswith("(") and bool(BENGALI_RE.search(line))


def page_lines(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8").splitlines()
    lines = [line.rstrip() for line in strip_headers(content)]
    return [line for line in lines if line.strip()]


def load_page_footnotes(pdf_path: Path, page_num: int) -> dict[int, str]:
    completed = subprocess.run(
        [
            "pdftotext",
            "-f",
            str(page_num),
            "-l",
            str(page_num),
            "-layout",
            str(pdf_path),
            "-",
        ],
        capture_output=True,
        check=True,
    )
    text = completed.stdout.decode("utf-8", errors="ignore")
    lines = text.splitlines()
    footer_start = None
    threshold = len(lines) // 3
    for idx, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if idx < threshold or not stripped:
            continue
        if re.match(r"^[0-9]{1,4}$", stripped) or re.match(r"^[0-9]{1,4}\s+.+$", stripped):
            footer_start = idx
            break
    if footer_start is None:
        return {}

    footnotes: dict[int, list[str]] = {}
    current_num: int | None = None
    for raw_line in lines[footer_start:]:
        stripped = raw_line.strip()
        if not stripped:
            continue
        if re.match(r"^[0-9]{1,4}$", stripped):
            current_num = int(stripped)
            footnotes.setdefault(current_num, [])
            continue
        match = re.match(r"^([0-9]{1,4})\s+(.*)$", stripped)
        if match:
            current_num = int(match.group(1))
            footnotes[current_num] = [normalize_text(match.group(2))]
            continue
        if current_num is not None:
            footnotes[current_num].append(normalize_text(stripped))
    return {key: normalize_text(" ".join(value)) for key, value in footnotes.items()}


def extract_trailing_footnotes(lines: Iterable[str]) -> list[int]:
    ids: list[int] = []
    for line in lines:
        stripped = line.strip()
        for match in FOOTNOTE_MARKER_RE.finditer(stripped):
            num = bengali_digits_to_int(match.group(1))
            if num is not None and num not in ids:
                ids.append(num)
    return ids


def parse_candidates(transcript_dir: Path) -> list[CandidateEntry]:
    current_section = ""
    current: CandidateEntry | None = None
    dua_seq = 0
    candidates: list[CandidateEntry] = []
    stop_after_current = False

    for page_num in range(PAGE_START, PAGE_END + 1):
        path = transcript_dir / f"page_{page_num:03d}.txt"
        if not path.exists():
            continue
        lines = page_lines(path)
        if lines == ["[[blank page]]"]:
            continue

        for raw_line in lines:
            line = normalize_text(raw_line)
            if not line:
                continue

            if any(line.startswith(prefix) for prefix in END_MATTER_PREFIXES):
                if current is not None:
                    candidates.append(current)
                    current = None
                stop_after_current = True
                break

            section_match = SECTION_RE.match(line)
            if section_match and "-" not in section_match.group(1):
                if current is not None:
                    candidates.append(current)
                    current = None
                current_section = line
                continue

            entry_match = ENTRY_RE.match(line)
            if entry_match and not SECTION_RE.match(line):
                marker = entry_match.group(1)
                if "-" in marker:
                    if current is not None and (
                        normalize_digits(marker) == normalize_digits(current.entry_number_bn)
                        or entry_base_number(marker) == entry_base_number(current.entry_number_bn)
                    ):
                        remainder = entry_match.group(2).strip()
                        if remainder:
                            current.raw_lines.append(remainder)
                        current.page_end = page_num
                        if page_num not in current.raw_pages:
                            current.raw_pages.append(page_num)
                        continue
                    if current is not None:
                        candidates.append(current)
                    dua_seq += 1
                    current = CandidateEntry(
                        dua_seq=dua_seq,
                        section_title_bn=current_section,
                        entry_number_bn=marker,
                        page_start=page_num,
                        page_end=page_num,
                        raw_lines=[],
                        raw_pages=[page_num],
                    )
                    remainder = entry_match.group(2).strip()
                    if remainder:
                        current.raw_lines.append(remainder)
                    continue

            subentry_match = SUBENTRY_RE.match(line)
            if (
                current is not None
                and subentry_match
                and "-(" in current.entry_number_bn
                and current.raw_lines
                and extract_trailing_footnotes([current.raw_lines[-1]])
            ):
                candidates.append(current)
                base_marker = current.entry_number_bn.split("-(", 1)[0]
                dua_seq += 1
                current = CandidateEntry(
                    dua_seq=dua_seq,
                    section_title_bn=current_section,
                    entry_number_bn=f"{base_marker}-({subentry_match.group(1)})",
                    page_start=page_num,
                    page_end=page_num,
                    raw_lines=[],
                    raw_pages=[page_num],
                )
                remainder = subentry_match.group(2).strip()
                if remainder:
                    current.raw_lines.append(remainder)
                continue

            if current is not None:
                current.raw_lines.append(line)
                current.page_end = page_num
                if page_num not in current.raw_pages:
                    current.raw_pages.append(page_num)

        if stop_after_current:
            break

    if current is not None:
        candidates.append(current)

    return candidates


def parse_candidate(entry: CandidateEntry, footnote_cache: dict[int, dict[int, str]]) -> DuaRow:
    arabic_lines: list[str] = []
    translit_lines: list[str] = []
    translation_lines: list[str] = []
    explicit_reference_lines: list[str] = []
    notes: list[str] = []

    in_translit = False
    in_reference = False
    translation_started = False
    prev_was_arabic = False
    for line in entry.raw_lines:
        if is_reference_line(line):
            explicit_reference_lines.append(normalize_text(line))
            in_reference = True
            in_translit = False
            prev_was_arabic = False
            continue

        if in_reference:
            if not ARABIC_RE.search(line) and not looks_like_translit(line) and not line.lstrip().startswith(("“", "\"", "'", "‘")):
                explicit_reference_lines.append(normalize_text(line))
                prev_was_arabic = False
                continue
            in_reference = False

        if ARABIC_RE.search(line):
            arabic_lines.append(normalize_text(line))
            in_translit = False
            prev_was_arabic = True
            continue

        if in_translit and line.lstrip().startswith(("“", "\"")) and BENGALI_RE.search(line):
            in_translit = False

        if (
            translation_started
            and line.lstrip().startswith("(")
            and BENGALI_RE.search(line)
            and not prev_was_arabic
            and not in_translit
        ):
            prev_was_arabic = False
            pass
        elif looks_like_translit(line):
            translit_lines.append(normalize_text(line).strip("()।. "))
            in_translit = not TRANSLIT_END_RE.search(line.rstrip())
            prev_was_arabic = False
            continue

        if in_translit and BENGALI_RE.search(line):
            translit_lines.append(normalize_text(line).strip("()।. "))
            if TRANSLIT_END_RE.search(line.rstrip()):
                in_translit = False
            prev_was_arabic = False
            continue

        inline_translit, line_for_translation = extract_inline_translit(line)
        if inline_translit and (not translit_lines or translit_lines[-1] != inline_translit):
            translit_lines.append(inline_translit)

        cleaned = clean_translation_line(line_for_translation)
        if cleaned and (not translation_lines or translation_lines[-1] != cleaned):
            translation_lines.append(cleaned)
            if arabic_lines or translit_lines or marks_translation_start(cleaned):
                translation_started = True
        prev_was_arabic = False

    explicit_reference_text = normalize_text(" ".join(explicit_reference_lines))
    reference_text = ""
    footnote_ids = extract_trailing_footnotes(entry.raw_lines)
    if footnote_ids:
        refs: list[str] = []
        pages_to_check = sorted(
            page_num
            for page_num in set(entry.raw_pages + [entry.page_start - 1, entry.page_end + 1])
            if PAGE_START <= page_num <= PAGE_END
        )
        for page_num in pages_to_check:
            if page_num not in footnote_cache:
                footnote_cache[page_num] = load_page_footnotes(PDF_PATH, page_num)
            page_refs = footnote_cache[page_num]
            for footnote_id in footnote_ids:
                if footnote_id in page_refs and page_refs[footnote_id] not in refs:
                    refs.append(page_refs[footnote_id])
        recovered_reference = normalize_text(" ".join(refs))
        if recovered_reference:
            reference_text = recovered_reference
            notes.append("reference_recovered_from_pdftext")
    if not reference_text:
        reference_text = explicit_reference_text
    if not reference_text and entry.entry_number_bn in MANUAL_REFERENCE_OVERRIDES:
        reference_text = MANUAL_REFERENCE_OVERRIDES[entry.entry_number_bn]
        notes.append("reference_recovered_manual_override")

    if entry.page_end > entry.page_start:
        notes.append("continued_from_previous_or_next_page")
    if not reference_text and footnote_ids:
        notes.append("missing_reference_text")

    excerpt = normalize_text(" ".join(entry.raw_lines[:4]))
    review_flag = ""
    if not arabic_lines and not translit_lines and not translation_lines:
        review_flag = "empty_content"
    elif not reference_text and footnote_ids:
        review_flag = "missing_reference"

    return DuaRow(
        dua_seq=entry.dua_seq,
        section_title_bn=entry.section_title_bn,
        page_start=entry.page_start,
        page_end=entry.page_end,
        entry_number_bn=entry.entry_number_bn,
        arabic=normalize_text(" ".join(arabic_lines)),
        transliteration_bn=normalize_text(" ".join(translit_lines)),
        translation_bn=normalize_translation_text(" ".join(translation_lines)),
        reference_bn=reference_text,
        notes=",".join(notes),
        raw_pages=",".join(str(page) for page in entry.raw_pages),
        parse_status="ok" if not review_flag else "needs_review",
        review_flag=review_flag,
        source_excerpt=excerpt[:300],
    )


def build_rows(transcript_dir: Path) -> list[DuaRow]:
    footnote_cache: dict[int, dict[int, str]] = {}
    candidates = parse_candidates(transcript_dir)
    return [parse_candidate(candidate, footnote_cache) for candidate in candidates]


def write_csv(rows: list[DuaRow], output_path: Path, review_path: Path) -> None:
    base_fields = [
        "dua_seq",
        "section_title_bn",
        "page_start",
        "page_end",
        "entry_number_bn",
        "arabic",
        "transliteration_bn",
        "translation_bn",
        "reference_bn",
        "notes",
    ]
    review_fields = base_fields + ["raw_pages", "parse_status", "review_flag", "source_excerpt"]

    with output_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=base_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in base_fields})

    with review_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=review_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in review_fields})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a dua-level Bengali Hisnul Muslim dataset from reviewed transcripts.")
    parser.add_argument("--transcript-dir", type=Path, default=TRANSCRIPT_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT_CSV)
    parser.add_argument("--review-output", type=Path, default=REVIEW_CSV)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(args.transcript_dir)
    write_csv(rows, args.output, args.review_output)
    print(f"Wrote {len(rows)} rows to {args.output}")
    print(f"Wrote review rows to {args.review_output}")


if __name__ == "__main__":
    main()
