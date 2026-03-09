from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TRANSCRIPT_DIR = SCRIPT_DIR / "page_transcripts_manual"
MANIFEST_PATH = TRANSCRIPT_DIR / "manifest.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize OCR transcript lines by trimming obvious Latin/digit garbage."
    )
    parser.add_argument("--page-start", type=int, default=39)
    parser.add_argument("--page-end", type=int, default=307)
    return parser.parse_args()


def is_script_char(char: str) -> bool:
    code = ord(char)
    return (
        0x0980 <= code <= 0x09FF
        or 0x0600 <= code <= 0x06FF
        or 0x0750 <= code <= 0x077F
        or 0x08A0 <= code <= 0x08FF
    )


def is_leading_keep_char(char: str) -> bool:
    return is_script_char(char) or char.isdigit()


def is_trailing_keep_char(char: str) -> bool:
    return is_script_char(char) or char.isdigit() or char in "\"'”’).।:;!?»-–,"


def trim_noise(line: str) -> str:
    stripped = line.strip()
    if not stripped:
        return ""

    bengali_like = sum(0x0980 <= ord(ch) <= 0x09FF for ch in stripped)
    digit_count = sum(ch.isdigit() for ch in stripped)

    if all(not is_script_char(ch) and not ch.isdigit() for ch in stripped):
        return ""
    if bengali_like <= 2 and digit_count >= 3:
        return ""

    start = 0
    while start < len(stripped) and not is_leading_keep_char(stripped[start]):
        start += 1
    stripped = stripped[start:]
    if not stripped:
        return ""

    end = len(stripped) - 1
    while end >= 0 and not is_trailing_keep_char(stripped[end]):
        end -= 1
    stripped = stripped[: end + 1]

    if any(0x0980 <= ord(ch) <= 0x09FF for ch in stripped):
        stripped = re.sub(r"\b[A-Za-z]{2,}\b", "", stripped)
        stripped = re.sub(r"\b\d{3,}\b", "", stripped)
        stripped = re.sub(r"\s{2,}", " ", stripped).strip()
    return stripped.strip()


def load_manifest() -> list[dict]:
    return [
        json.loads(line)
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> None:
    args = parse_args()
    for row in load_manifest():
        page_num = int(row["page_num"])
        if not (args.page_start <= page_num <= args.page_end):
            continue
        transcript_path = TRANSCRIPT_DIR / row["transcript_file"]
        lines = transcript_path.read_text(encoding="utf-8").splitlines()
        if len(lines) < 2:
            continue
        header = lines[:2]
        body_lines = [trim_noise(line) for line in lines[3:]]
        normalized = []
        previous_blank = False
        for line in body_lines:
            blank = line == ""
            if blank and previous_blank:
                continue
            normalized.append(line)
            previous_blank = blank
        while normalized and normalized[0] == "":
            normalized.pop(0)
        while normalized and normalized[-1] == "":
            normalized.pop()

        transcript_path.write_text(
            "\n".join(header) + "\n\n" + "\n".join(normalized) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
