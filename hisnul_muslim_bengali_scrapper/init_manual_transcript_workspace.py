from __future__ import annotations

import argparse
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_RENDERED_DIR = SCRIPT_DIR / "rendered_pages"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "page_transcripts_manual"
DEFAULT_BATCH_SIZE = 8
DEFAULT_PILOT_START = 23
DEFAULT_PILOT_END = 30


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a manual transcript workspace from rendered page images."
    )
    parser.add_argument("--rendered-dir", type=Path, default=DEFAULT_RENDERED_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--pilot-start", type=int, default=DEFAULT_PILOT_START)
    parser.add_argument("--pilot-end", type=int, default=DEFAULT_PILOT_END)
    parser.add_argument(
        "--overwrite-existing",
        action="store_true",
        help="Replace transcript templates that already exist.",
    )
    return parser.parse_args()


def load_render_manifest(rendered_dir: Path) -> list[dict]:
    manifest_path = rendered_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Rendered manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, list) or not manifest:
        raise RuntimeError("Rendered manifest is empty or malformed.")
    return manifest


def chunk_pages(page_nums: list[int], batch_size: int) -> list[list[int]]:
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    return [page_nums[i : i + batch_size] for i in range(0, len(page_nums), batch_size)]


def build_batch_lookup(page_nums: list[int], batch_size: int) -> dict[int, str]:
    lookup: dict[int, str] = {}
    for chunk in chunk_pages(page_nums, batch_size):
        batch_id = f"batch_{chunk[0]:03d}_{chunk[-1]:03d}"
        for page_num in chunk:
            lookup[page_num] = batch_id
    return lookup


def build_transcript_stub(page_num: int, image_name: str) -> str:
    return (
        f"PAGE: {page_num:03d}\n"
        f"SOURCE_IMAGE: {image_name}\n"
        "\n"
    )


def write_readme(output_dir: Path) -> None:
    readme = """# Manual Page Transcripts

Each `page_XXX.txt` file is the manual transcript for one rendered page image.

Rules:
- Preserve visible wording exactly as printed.
- Keep chapter headings, numbering, Arabic, Bengali transliteration, Bengali translation, and references.
- Omit obvious page chrome such as page numbers and decorative header/footer noise.
- Do not guess missing text. Use `[[unclear]]` for unreadable spans.
- Keep visible block spacing with blank lines where it helps recover layout later.
- If a dua continues across pages, transcribe only what is visible on the current page.
"""
    (output_dir / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    args = parse_args()
    rendered_dir = args.rendered_dir
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_render_manifest(rendered_dir)
    page_nums = [int(entry["page_num"]) for entry in manifest]
    batch_lookup = build_batch_lookup(page_nums, args.batch_size)

    transcript_manifest = []
    for entry in manifest:
        page_num = int(entry["page_num"])
        image_name = str(entry["file_name"])
        transcript_name = f"page_{page_num:03d}.txt"
        transcript_path = output_dir / transcript_name
        if args.overwrite_existing or not transcript_path.exists():
            transcript_path.write_text(
                build_transcript_stub(page_num, image_name),
                encoding="utf-8",
            )

        transcript_manifest.append(
            {
                "page_num": page_num,
                "image_file": image_name,
                "transcript_file": transcript_name,
                "batch_id": batch_lookup[page_num],
                "status": "pending",
                "notes": "",
                "is_pilot": args.pilot_start <= page_num <= args.pilot_end,
            }
        )

    manifest_path = output_dir / "manifest.jsonl"
    with manifest_path.open("w", encoding="utf-8") as handle:
        for row in transcript_manifest:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    write_readme(output_dir)

    print(f"Prepared transcript workspace in {output_dir}")
    print(f"Pages: {len(transcript_manifest)}")
    print(
        f"Pilot batch: pages {args.pilot_start}-{args.pilot_end}; "
        f"batch size: {args.batch_size}"
    )


if __name__ == "__main__":
    main()
