from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PDF_PATH = SCRIPT_DIR / "bn_Hisnul_Elmuslim.pdf"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "rendered_pages"
DEFAULT_PAGE_START = 23


def run_command(args: list[str]) -> str:
    completed = subprocess.run(args, capture_output=True, check=True)
    return completed.stdout.decode("utf-8", errors="ignore")


def extract_pdf_page_count(pdf_path: Path) -> int:
    info = run_command(["pdfinfo", str(pdf_path)])
    for line in info.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError("Could not determine PDF page count.")


def render_page(pdf_path: Path, output_dir: Path, page_num: int, dpi: int) -> Path:
    prefix = output_dir / f"page_{page_num:03d}"
    subprocess.run(
        [
            "pdftocairo",
            "-f",
            str(page_num),
            "-l",
            str(page_num),
            "-singlefile",
            "-png",
            "-r",
            str(dpi),
            str(pdf_path),
            str(prefix),
        ],
        check=True,
        capture_output=True,
    )
    image_path = prefix.with_suffix(".png")
    if not image_path.exists():
        raise RuntimeError(f"Failed to render page {page_num}")
    return image_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render PDF pages to PNG images.")
    parser.add_argument("--page-start", type=int, default=DEFAULT_PAGE_START)
    parser.add_argument("--page-end", type=int, default=None)
    parser.add_argument("--dpi", type=int, default=220)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    page_end = args.page_end or extract_pdf_page_count(PDF_PATH)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    for page_num in range(args.page_start, page_end + 1):
        image_path = render_page(PDF_PATH, output_dir, page_num, args.dpi)
        manifest.append(
            {
                "page_num": page_num,
                "file_name": image_path.name,
                "dpi": args.dpi,
            }
        )
        print(f"Rendered page {page_num}")

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {len(manifest)} pages to {output_dir}")


if __name__ == "__main__":
    main()
