# Communication Style

Windows-first Python Typer CLI for building a local communication style guide
from your own Microsoft 365 messages through delegated Microsoft Graph access.

Project repo: <https://github.com/Midtown-Technology-Group/communication-style>

The tool follows the same shape as Midtown's other Graph toys: Typer CLI,
shared `mtg-microsoft-auth` WAM authentication, local token cache reuse, and
explicit per-tool environment variables.

## What This Is

- A local-only collector for your authored sent email and Teams chat messages.
- A markdown generator for `COMMUNICATION_STYLE.md`.
- Era and participant-focused report generation.
- A read-only Graph tool by default.
- A local analysis workflow that keeps generated corpus/docs under
  `%USERPROFILE%\.codex\communication-style` by default.

## What This Is Not

- It is not a tenant-wide Teams export tool.
- It does not use application permissions.
- It does not pull channel messages yet.
- It does not send raw message content to an LLM provider.
- It does not guarantee Teams participant metadata. Current delegated Graph
  access can read chat messages, but historical chat member lookups may fail;
  participant-focused reports therefore use Sent Items recipients plus Teams
  chat or meeting titles unless explicitly told to try member lookups.

## Graph Permissions

Default delegated scopes:

```powershell
User.Read,Mail.Read,Chat.Read
```

Optional later scopes:

- `offline_access`: only for unattended repeat refresh.
- `ChannelMessage.Read.All`: only if channel posts are explicitly in scope.
- `Mail.Read.Shared`: only if shared mailbox sent items are explicitly in scope.

The tool intentionally avoids `/users/{id}/chats/getAllMessages` because
Microsoft exposes that bulk Teams export shape as application-permission only.
Instead it walks `/me/chats` and `/me/chats/{chat-id}/messages`, then keeps only
messages authored by the signed-in user.

## Setup

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .[dev]
```

## Auth

Set these environment variables if you need to override defaults:

- `COMM_STYLE_CLIENT_ID` defaults to the shared Midtown public client.
- `COMM_STYLE_TENANT_ID` defaults to `common`.
- `COMM_STYLE_SCOPES` defaults to `User.Read,Mail.Read,Chat.Read`.
- `COMM_STYLE_AUTH_MODE` defaults to `wam`.
- `COMM_STYLE_ALLOW_BROKER` defaults to `true`.
- `MTG_AUTH_ACCOUNT_HINT` can pin the preferred signed-in UPN.
- `COMM_STYLE_OUTPUT_DIR` defaults to `%USERPROFILE%\.codex\communication-style`.

## Usage

Collect a local corpus:

```powershell
.\invoke.ps1 collect --mail-limit 250 --chat-limit 50 --chat-message-limit 500
```

Generate the style guide:

```powershell
.\invoke.ps1 generate
```

Generate era-specific reports:

```powershell
.\invoke.ps1 eras
```

Generate participant-focused reports:

```powershell
.\invoke.ps1 focus
```

`focus` currently includes built-in cuts for Jack Musick, Steven Keath, and
company ownership. Add `--fetch-chat-members` if you want to probe the Teams
members endpoint anyway; the default avoids slow failures on historical chat
IDs.

Outputs:

- `%USERPROFILE%\.codex\communication-style\communication-samples.jsonl`
- `%USERPROFILE%\.codex\communication-style\summary.json`
- `%USERPROFILE%\.codex\communication-style\COMMUNICATION_STYLE.md`
- `%USERPROFILE%\.codex\communication-style\COMMUNICATION_STYLE_PROFILE.md`
- `%USERPROFILE%\.codex\communication-style\eras\`
- `%USERPROFILE%\.codex\communication-style\focused\`

## Development

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Release

Initial toy release is `v0.1.0`.

## License

GPL-3.0-or-later.
