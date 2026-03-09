from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import requests


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PDF_PATH = SCRIPT_DIR / "bn_Hisnul_Elmuslim.pdf"
PAGE_START = 23
MODEL_NAME = "gemini-2.0-flash"
TEXT_OUTPUT_DIR = SCRIPT_DIR / "page_text_gemini"
RAW_OUTPUT_DIR = SCRIPT_DIR / "page_text_gemini_raw"


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_environment() -> None:
    load_env_file(REPO_ROOT / ".env")
    load_env_file(SCRIPT_DIR / ".env")


def get_api_key() -> str:
    load_environment()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set. Put it in .env or export it in the shell.")
    return api_key


def run_command(args: list[str]) -> str:
    completed = subprocess.run(args, capture_output=True, check=True)
    return completed.stdout.decode("utf-8", errors="ignore")


def extract_pdf_page_count(pdf_path: Path) -> int:
    info = run_command(["pdfinfo", str(pdf_path)])
    for line in info.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError("Could not determine PDF page count.")


def render_page_image(pdf_path: Path, page_num: int, output_dir: Path) -> Path:
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


def build_prompt(page_num: int) -> str:
    return (
        f"You are extracting text from page {page_num} of a Bengali/Arabic Islamic book. "
        "Transcribe the page faithfully. Preserve line breaks where they help readability. "
        "Keep Arabic, Bengali, transliteration, numbering, and references exactly as visible. "
        "Do not summarize, translate, normalize, or explain anything. "
        "Return plain text only."
    )


def call_gemini_for_page(
    image_path: Path,
    page_num: int,
    api_key: str,
    *,
    model_name: str,
    max_retries: int,
) -> dict:
    image_b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": build_prompt(page_num)},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_b64,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "topP": 0.95,
            "maxOutputTokens": 8192,
        },
    }
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model_name}:generateContent?key={api_key}"
    )
    backoff_seconds = 5.0

    for attempt in range(max_retries + 1):
        response = requests.post(url, json=payload, timeout=180)
        if response.status_code < 400:
            return response.json()

        if response.status_code not in {429, 500, 503} or attempt == max_retries:
            message = response.text[:1000]
            raise RuntimeError(
                f"Gemini request failed for page {page_num} with status "
                f"{response.status_code}: {message}"
            )

        time.sleep(backoff_seconds)
        backoff_seconds *= 2

    raise RuntimeError(f"Gemini request failed for page {page_num} after retries.")


def extract_text_from_response(response_json: dict) -> str:
    candidates = response_json.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini response contained no candidates.")

    parts = candidates[0].get("content", {}).get("parts", [])
    text_chunks = [part.get("text", "") for part in parts if part.get("text")]
    text = "\n".join(chunk.strip() for chunk in text_chunks if chunk.strip()).strip()
    if not text:
        raise RuntimeError("Gemini response contained no text.")
    return text


def write_page_outputs(page_num: int, text: str, response_json: dict) -> None:
    TEXT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    (TEXT_OUTPUT_DIR / f"page_{page_num:03d}.txt").write_text(text, encoding="utf-8")
    (RAW_OUTPUT_DIR / f"page_{page_num:03d}.json").write_text(
        json.dumps(response_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract PDF pages to text with Gemini.")
    parser.add_argument("--page-start", type=int, default=PAGE_START)
    parser.add_argument("--page-end", type=int, default=None)
    parser.add_argument("--sleep-seconds", type=float, default=2.0)
    parser.add_argument("--model", default=MODEL_NAME)
    parser.add_argument("--max-retries", type=int, default=4)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    api_key = get_api_key()
    page_end = args.page_end or extract_pdf_page_count(PDF_PATH)

    with tempfile.TemporaryDirectory(prefix="bn_hisn_gemini_") as temp_dir_name:
        temp_dir = Path(temp_dir_name)

        for page_num in range(args.page_start, page_end + 1):
            if args.resume and (TEXT_OUTPUT_DIR / f"page_{page_num:03d}.txt").exists():
                print(f"Skipping page {page_num}; text file already exists")
                continue
            image_path = render_page_image(PDF_PATH, page_num, temp_dir)
            response_json = call_gemini_for_page(
                image_path,
                page_num,
                api_key,
                model_name=args.model,
                max_retries=args.max_retries,
            )
            text = extract_text_from_response(response_json)
            write_page_outputs(page_num, text, response_json)
            print(f"Saved page {page_num}")
            if args.sleep_seconds:
                time.sleep(args.sleep_seconds)


if __name__ == "__main__":
    main()
