from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from communication_style.generator import build_human_report, build_style_markdown
from communication_style.models import CommunicationSample


@dataclass(frozen=True)
class Era:
    slug: str
    title: str
    samples: list[CommunicationSample]


def build_eras(samples: list[CommunicationSample]) -> list[Era]:
    dated = [sample for sample in samples if _created_year(sample)]
    old_tenure = [
        sample
        for sample in dated
        if _created_year(sample) in {"2018", "2019", "2020", "2021", "2022", "2023"}
    ]
    return_period = [sample for sample in dated if _created_year(sample) == "2026"]
    eras = [
        Era("old-tenure-2018-2023", "Old MTG Tenure (2018-2023)", old_tenure),
        Era("return-period-2026", "Return Period (2026)", return_period),
    ]
    year_counts = Counter(_created_year(sample) for sample in dated)
    for year in sorted(year for year, count in year_counts.items() if count >= 100):
        eras.append(
            Era(
                year,
                year,
                [sample for sample in dated if _created_year(sample) == year],
            )
        )
    return [era for era in eras if era.samples]


def write_era_outputs(
    samples: list[CommunicationSample], output_dir: Path, *, min_samples: int = 100
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    eras = build_eras(samples)
    index_lines = [
        "# Communication Style Eras",
        "",
        "These files split the communication-style corpus by time period. Use this to distinguish durable voice from role-era habits.",
        "",
        "## Era Outputs",
        "",
    ]
    for era in eras:
        if len(era.samples) < min_samples:
            continue
        agent_path = output_dir / f"{era.slug}_COMMUNICATION_STYLE.md"
        human_path = output_dir / f"{era.slug}_PROFILE.md"
        agent_path.write_text(
            build_style_markdown(
                era.samples, title=f"{era.title} Communication Style Instructions"
            ),
            encoding="utf-8",
        )
        human_path.write_text(
            build_human_report(
                era.samples, title=f"{era.title} Communication Style Profile"
            ),
            encoding="utf-8",
        )
        source_counts = Counter(sample.source for sample in era.samples)
        index_lines.extend(
            [
                f"### {era.title}",
                "",
                f"- Samples: {len(era.samples)}",
                f"- Sent email: {source_counts.get('sent-mail', 0)}",
                f"- Teams chat: {source_counts.get('teams-chat', 0)}",
                f"- Agent-facing: `{agent_path.name}`",
                f"- Human-facing: `{human_path.name}`",
                "",
            ]
        )
    index_path = output_dir / "README.md"
    index_path.write_text("\n".join(index_lines), encoding="utf-8")
    return index_path


def _created_year(sample: CommunicationSample) -> str | None:
    if not sample.created:
        return None
    try:
        return str(datetime.fromisoformat(sample.created.replace("Z", "+00:00")).year)
    except ValueError:
        return sample.created[:4] if len(sample.created) >= 4 else None
