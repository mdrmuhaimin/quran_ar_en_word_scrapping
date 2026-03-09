from __future__ import annotations

import argparse
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TRANSCRIPT_DIR = SCRIPT_DIR / "page_transcripts_manual"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate manual page transcript workspace coverage."
    )
    parser.add_argument("--transcript-dir", type=Path, default=DEFAULT_TRANSCRIPT_DIR)
    return parser.parse_args()


def load_manifest(transcript_dir: Path) -> list[dict]:
    manifest_path = transcript_dir / "manifest.jsonl"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Transcript manifest not found: {manifest_path}")

    rows = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    if not rows:
        raise RuntimeError("Transcript manifest is empty.")
    return rows


def validate_header(path: Path, page_num: int, image_file: str) -> list[str]:
    errors = []
    content = path.read_text(encoding="utf-8")
    expected_prefix = f"PAGE: {page_num:03d}\nSOURCE_IMAGE: {image_file}\n"
    if not content.startswith(expected_prefix):
        errors.append(f"Header mismatch in {path.name}")
    return errors


def main() -> None:
    args = parse_args()
    transcript_dir = args.transcript_dir
    rows = load_manifest(transcript_dir)

    errors: list[str] = []
    pilot_pages = 0
    for row in rows:
        page_num = int(row["page_num"])
        transcript_path = transcript_dir / row["transcript_file"]
        if not transcript_path.exists():
            errors.append(f"Missing transcript file for page {page_num}")
            continue
        errors.extend(validate_header(transcript_path, page_num, row["image_file"]))
        if row.get("is_pilot"):
            pilot_pages += 1

    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)

    print(f"Validated {len(rows)} transcript files in {transcript_dir}")
    print(f"Pilot pages flagged: {pilot_pages}")


if __name__ == "__main__":
    main()
