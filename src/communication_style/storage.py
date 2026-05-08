from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from communication_style.models import CollectionSummary, CommunicationSample


def write_jsonl(path: Path, samples: list[CommunicationSample]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(json.dumps(sample.to_dict(), ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[CommunicationSample]:
    samples: list[CommunicationSample] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw = json.loads(line)
            samples.append(CommunicationSample(**raw))
    return samples


def write_summary(path: Path, summary: CollectionSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(summary), indent=2), encoding="utf-8")
