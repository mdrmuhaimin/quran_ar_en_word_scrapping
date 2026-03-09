from __future__ import annotations

import json
import os
from pathlib import Path

import requests


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_MODEL = "gemini-2.0-flash"


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
        raise RuntimeError("GOOGLE_API_KEY is not set.")
    return api_key


def print_response(label: str, response: requests.Response) -> None:
    print(f"\n== {label} ==")
    print(f"HTTP {response.status_code}")
    print(response.text[:4000])


def list_models(api_key: str) -> None:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    response = requests.get(url, timeout=60)
    print_response("ListModels", response)

    if response.ok:
        payload = response.json()
        models = payload.get("models", [])
        print("\nSupported models with generateContent:")
        for model in models:
            methods = model.get("supportedGenerationMethods", [])
            if "generateContent" in methods:
                print("-", model.get("name"))


def probe_generate_content(api_key: str, model: str) -> None:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Reply with exactly the single word OK."
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 8,
        },
    }
    response = requests.post(url, json=payload, timeout=60)
    print_response(f"GenerateContent ({model})", response)


def main() -> None:
    api_key = get_api_key()
    list_models(api_key)
    probe_generate_content(api_key, DEFAULT_MODEL)


if __name__ == "__main__":
    main()
