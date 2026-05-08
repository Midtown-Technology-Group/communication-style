from __future__ import annotations

from pathlib import Path

import typer
from mtg_microsoft_auth import GraphAuthSession, GraphClient
from rich.console import Console

from communication_style.config import default_output_dir, load_auth_config
from communication_style.focus import write_focus_outputs
from communication_style.generator import build_human_report, build_style_markdown
from communication_style.eras import write_era_outputs
from communication_style.repository import CommunicationRepository
from communication_style.storage import read_jsonl, write_jsonl, write_summary
from communication_style.models import CollectionSummary

app = typer.Typer(
    help="Build a local communication style guide from delegated Microsoft Graph data."
)
console = Console()


def build_repository() -> CommunicationRepository:
    session = GraphAuthSession(load_auth_config())
    client = GraphClient(session)
    return CommunicationRepository(client)


def _friendly_error(exc: Exception) -> None:
    message = str(exc)
    if "Unable to acquire Microsoft Graph access token" in message:
        raise typer.Exit(_print_auth_help()) from exc
    console.print(f"[red]Error:[/red] {message}")
    raise typer.Exit(1) from exc


def _print_auth_help() -> int:
    console.print(
        "[red]Unable to acquire a Microsoft Graph token for communication-style.[/red]"
    )
    console.print("Current default delegated scopes: User.Read,Mail.Read,Chat.Read")
    console.print("Try setting the tenant and account hint, then rerun the command:")
    console.print(
        "$env:COMM_STYLE_TENANT_ID='a3599b15-c39c-4b41-a219-7e24dd5b5190'; "
        "$env:MTG_AUTH_ACCOUNT_HINT='your.upn@midtowntg.com'"
    )
    console.print(
        "If other MTG toys are signed in but this still fails, the shared Entra app likely needs "
        "these delegated scopes consented for this tool."
    )
    return 1


@app.command("collect")
def collect(
    output_dir: Path = typer.Option(default_output_dir(), "--output-dir", "-o"),
    mail_limit: int = typer.Option(250, "--mail-limit", min=0),
    chat_limit: int = typer.Option(50, "--chat-limit", min=0),
    chat_message_limit: int = typer.Option(500, "--chat-message-limit", min=0),
    full: bool = typer.Option(
        False,
        "--full",
        help="Walk all available Sent Items, chats, and chat-message pages.",
    ),
    include_chats: bool = typer.Option(True, "--include-chats/--no-chats"),
    include_mail: bool = typer.Option(True, "--include-mail/--no-mail"),
) -> None:
    try:
        repo = build_repository()
        repo.progress = lambda label, page, count: console.print(
            f"{label}: page {page}, {count} seen"
        )
        me = repo.current_user()
    except Exception as exc:
        _friendly_error(exc)
        return
    user_id = me["id"]
    samples = []
    mail_count = 0
    chat_count = 0
    effective_mail_limit = None if full else mail_limit
    effective_chat_limit = None if full else chat_limit
    effective_chat_message_limit = None if full else chat_message_limit
    if include_mail and (full or mail_limit):
        try:
            mail_samples = repo.sent_mail(limit=effective_mail_limit)
        except Exception as exc:
            _friendly_error(exc)
            return
        mail_count = len(mail_samples)
        samples.extend(mail_samples)
    if include_chats and (full or (chat_limit and chat_message_limit)):
        try:
            chat_samples = repo.authored_chat_messages(
                user_id=user_id,
                chat_limit=effective_chat_limit,
                message_limit=effective_chat_message_limit,
            )
        except Exception as exc:
            _friendly_error(exc)
            return
        chat_count = len(chat_samples)
        samples.extend(chat_samples)

    output_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = output_dir / "communication-samples.jsonl"
    summary_path = output_dir / "summary.json"
    write_jsonl(corpus_path, samples)
    write_summary(
        summary_path,
        CollectionSummary.now(
            user_id=user_id,
            user_principal_name=me.get("userPrincipalName"),
            mail_samples=mail_count,
            chat_samples=chat_count,
            output_path=str(corpus_path),
        ),
    )
    console.print(f"Wrote {len(samples)} samples to {corpus_path}")
    console.print(f"Wrote summary to {summary_path}")


@app.command("generate")
def generate(
    corpus: Path = typer.Option(
        default_output_dir() / "communication-samples.jsonl", "--corpus", "-c"
    ),
    output: Path = typer.Option(
        default_output_dir() / "COMMUNICATION_STYLE.md", "--output", "-o"
    ),
    human_output: Path = typer.Option(
        default_output_dir() / "COMMUNICATION_STYLE_PROFILE.md", "--human-output"
    ),
) -> None:
    samples = read_jsonl(corpus)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_style_markdown(samples), encoding="utf-8")
    console.print(f"Wrote style instructions to {output}")
    human_output.parent.mkdir(parents=True, exist_ok=True)
    human_output.write_text(build_human_report(samples), encoding="utf-8")
    console.print(f"Wrote human-facing profile to {human_output}")


@app.command("eras")
def eras(
    corpus: Path = typer.Option(
        default_output_dir() / "communication-samples.jsonl", "--corpus", "-c"
    ),
    output_dir: Path = typer.Option(
        default_output_dir() / "eras", "--output-dir", "-o"
    ),
) -> None:
    samples = read_jsonl(corpus)
    index_path = write_era_outputs(samples, output_dir)
    console.print(f"Wrote era index to {index_path}")


@app.command("focus")
def focus(
    corpus: Path = typer.Option(
        default_output_dir() / "communication-samples.jsonl", "--corpus", "-c"
    ),
    output_dir: Path = typer.Option(
        default_output_dir() / "focused", "--output-dir", "-o"
    ),
    refresh_mail: bool = typer.Option(True, "--refresh-mail/--no-refresh-mail"),
    fetch_chat_members: bool = typer.Option(
        False, "--fetch-chat-members/--no-fetch-chat-members"
    ),
) -> None:
    samples = read_jsonl(corpus)
    try:
        repo = build_repository()
        repo.progress = lambda label, page, count: console.print(
            f"{label}: page {page}, {count} seen"
        )
        index_path = write_focus_outputs(
            samples,
            output_dir,
            repo=repo,
            refresh_mail=refresh_mail,
            fetch_chat_members=fetch_chat_members,
        )
    except Exception as exc:
        _friendly_error(exc)
        return
    console.print(f"Wrote participant focus index to {index_path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
