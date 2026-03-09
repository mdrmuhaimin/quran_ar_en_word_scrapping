from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = SCRIPT_DIR / "page_transcripts_manual" / "manifest.jsonl"


def main() -> None:
    rows = [
        json.loads(line)
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    status_counts = Counter(row["status"] for row in rows)
    batch_counts: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        batch_counts[row["batch_id"]][row["status"]] += 1

    print("Status counts:")
    for status, count in sorted(status_counts.items()):
        print(f"- {status}: {count}")

    print("\nBatches:")
    for batch_id in sorted(batch_counts):
        counts = batch_counts[batch_id]
        summary = ", ".join(f"{k}={counts[k]}" for k in sorted(counts))
        print(f"- {batch_id}: {summary}")


if __name__ == "__main__":
    main()
