from __future__ import annotations

import re
from dataclasses import dataclass, replace
from pathlib import Path

from communication_style.generator import build_human_report, build_style_markdown
from communication_style.models import CommunicationSample


@dataclass(frozen=True)
class FocusGroup:
    name: str
    slug: str
    aliases: tuple[str, ...]
    note: str


FOCUS_GROUPS = (
    FocusGroup(
        name="Jack Musick",
        slug="jack-musick",
        aliases=("jack", "jack musick", "musick"),
        note="Friend and colleague.",
    ),
    FocusGroup(
        name="Steven Keath",
        slug="steven-keath",
        aliases=("steven", "steve", "steven keath", "keath"),
        note="Manager.",
    ),
    FocusGroup(
        name="Company Ownership",
        slug="company-ownership",
        aliases=("eric", "mike", "michael", "doug", "douglas"),
        note="Company ownership: Eric, Mike, and Doug.",
    ),
)


def write_focus_outputs(
    samples: list[CommunicationSample],
    output_dir: Path,
    *,
    repo=None,
    refresh_mail: bool = True,
    fetch_chat_members: bool = False,
) -> Path:
    enriched = enrich_participants(
        samples,
        repo=repo,
        refresh_mail=refresh_mail,
        fetch_chat_members=fetch_chat_members,
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Participant-Focused Communication Style Cuts",
        "",
        "These reports filter the local corpus by sent-mail recipient metadata plus Teams chat or meeting titles. They do not infer participants from message text.",
        "",
        "| Focus | Samples | Teams | Mail | Notes | Files |",
        "|---|---:|---:|---:|---|---|",
    ]

    for group in FOCUS_GROUPS:
        focused = filter_by_participants(enriched, group.aliases)
        teams = sum(1 for sample in focused if sample.source == "teams-chat")
        mail = sum(1 for sample in focused if sample.source == "sent-mail")
        if focused:
            instruction_name = f"{group.slug}_COMMUNICATION_STYLE.md"
            profile_name = f"{group.slug}_PROFILE.md"
            instruction_path = output_dir / instruction_name
            profile_path = output_dir / profile_name
            instruction_path.write_text(
                build_style_markdown(
                    focused,
                    title=f"Thomas with {group.name} Communication Style Instructions",
                ),
                encoding="utf-8",
            )
            profile_path.write_text(
                build_human_report(
                    focused,
                    title=f"Thomas with {group.name} Communication Style Profile",
                ),
                encoding="utf-8",
            )
            files = f"[instructions]({instruction_name}), [profile]({profile_name})"
        else:
            files = "No matching samples"
        lines.append(
            f"| {group.name} | {len(focused)} | {teams} | {mail} | {group.note} | {files} |"
        )

    index_path = output_dir / "README.md"
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return index_path


def enrich_participants(
    samples: list[CommunicationSample],
    *,
    repo=None,
    refresh_mail: bool = True,
    fetch_chat_members: bool = False,
) -> list[CommunicationSample]:
    enriched = list(samples)
    if repo is None:
        return enriched

    chat_member_cache: dict[str, list[str]] = {}
    updated: list[CommunicationSample] = []
    for sample in enriched:
        if (
            fetch_chat_members
            and sample.source == "teams-chat"
            and sample.conversation_id
            and not sample.participants
        ):
            members = chat_member_cache.get(sample.conversation_id)
            if members is None:
                members = repo.chat_members(sample.conversation_id)
                chat_member_cache[sample.conversation_id] = members
            updated.append(replace(sample, participants=members))
        else:
            updated.append(sample)

    if not refresh_mail:
        return updated

    mail_by_id = {sample.id: sample for sample in repo.sent_mail(limit=None)}
    refreshed: list[CommunicationSample] = []
    for sample in updated:
        replacement = mail_by_id.get(sample.id)
        if sample.source == "sent-mail" and replacement and replacement.participants:
            refreshed.append(replace(sample, participants=replacement.participants))
        else:
            refreshed.append(sample)
    return refreshed


def filter_by_participants(
    samples: list[CommunicationSample], aliases: tuple[str, ...]
) -> list[CommunicationSample]:
    return [
        sample
        for sample in samples
        if participant_matches(sample.participants, aliases)
        or participant_matches([sample.subject or ""], aliases)
    ]


def participant_matches(participants: list[str], aliases: tuple[str, ...]) -> bool:
    haystack = "\n".join(participants).lower()
    return any(_alias_matches(haystack, alias) for alias in aliases)


def _alias_matches(haystack: str, alias: str) -> bool:
    terms = [re.escape(term) for term in alias.lower().split()]
    pattern = r"\b" + r"\s+".join(terms) + r"\b"
    return re.search(pattern, haystack) is not None
