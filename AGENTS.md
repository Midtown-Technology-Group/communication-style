# Communication Style

Windows-first Python/Typer CLI that builds local communication-style Markdown from the signed-in user's sent mail and Teams chat messages. Implementation lives in `src/communication_style/`, tests in `tests/`; `invoke.ps1` wraps the installed CLI. Read [README.md](README.md) for collection limits, output paths, and delegated Graph permissions.

## Verification

Use Python 3.10+ and a virtual environment. From root: `python -m pip install -e ".[dev]"`, then `python -m pytest`, matching the CI dependency/test lane. Keep generator/text/focus tests independent of live Graph authentication through existing test seams. `invoke.ps1` is the operator entrypoint; installing shared `mtg-microsoft-auth` from its declared Git dependency requires network access.

## Data and authentication boundaries

Use shared `mtg-microsoft-auth` WAM and the established cache/account-hint configuration; do not build a second token cache or change shared app registration to solve a local issue. Default delegated scopes are `User.Read,Mail.Read,Chat.Read`. Additional refresh, shared-mailbox, or channel scopes need a concrete authorized use case.

Keep collection scoped to messages authored by the signed-in user. Walk `/me/chats` and per-chat messages; do not substitute application-permission bulk tenant exports. The tool does not send raw content to LLM providers. Preserve that boundary when adding analysis features.

Corpus and generated guides default under `%USERPROFILE%/.codex/communication-style`; keep message text, identity metadata, and auth material out of Git and diagnostic output. Use fixtures or temporary output directories for development, never a colleague's corpus.

Historical chat-member lookups can fail. Preserve the default focus behavior using sent recipients and chat/meeting titles; member probing is explicit. Source tests do not prove live consent, mailbox access, corpus completeness, or style accuracy. Document those limits when reporting operator results. Windows MSI releases and Graph collection are distinct operations from local verification.
