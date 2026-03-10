from __future__ import annotations

import argparse
import csv
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = SCRIPT_DIR / "bn_hisnul_dua_dataset.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the Bengali Hisnul Muslim dua dataset.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.dataset.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    required = {
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
    }
    if not rows:
        raise SystemExit("Dataset is empty.")
    missing_cols = required.difference(rows[0].keys())
    if missing_cols:
        raise SystemExit(f"Missing columns: {sorted(missing_cols)}")

    errors: list[str] = []
    seen = set()
    missing_arabic = 0
    missing_translit = 0
    missing_translation = 0
    missing_reference = 0
    recovered_reference = 0

    prev_seq = 0
    for row in rows:
        seq = int(row["dua_seq"])
        page_start = int(row["page_start"])
        page_end = int(row["page_end"])
        key = (row["entry_number_bn"], row["page_start"], row["page_end"])

        if seq <= prev_seq:
            errors.append(f"dua_seq not strictly increasing at {seq}")
        prev_seq = seq

        if page_end < page_start:
            errors.append(f"page range inverted for dua_seq={seq}")
        if key in seen:
            errors.append(f"duplicate row key for dua_seq={seq}: {key}")
        seen.add(key)

        if not row["section_title_bn"]:
            errors.append(f"missing section title for dua_seq={seq}")
        if not any(row[field].strip() for field in ("arabic", "transliteration_bn", "translation_bn")):
            errors.append(f"all content fields empty for dua_seq={seq}")
        if row["arabic"].strip() == "" and row["transliteration_bn"].strip() == "" and row["translation_bn"].strip().startswith("বুখারী"):
            errors.append(f"reference-only row for dua_seq={seq}")

        missing_arabic += int(not row["arabic"].strip())
        missing_translit += int(not row["transliteration_bn"].strip())
        missing_translation += int(not row["translation_bn"].strip())
        missing_reference += int(not row["reference_bn"].strip())
        recovered_reference += int("reference_recovered_from_pdftext" in row["notes"])

    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)

    print(f"Validated {len(rows)} dua rows in {args.dataset}")
    print(f"Rows missing arabic: {missing_arabic}")
    print(f"Rows missing transliteration_bn: {missing_translit}")
    print(f"Rows missing translation_bn: {missing_translation}")
    print(f"Rows missing reference_bn: {missing_reference}")
    print(f"Rows with recovered references: {recovered_reference}")


if __name__ == "__main__":
    main()
