from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

from mtg_microsoft_auth import AuthConfig, AuthMode

DEFAULT_CACHE_NAMESPACE = "mtg-shared-microsoft-auth"
DEFAULT_CLIENT_ID = "e02be6f7-063a-46a6-b2cc-109d5f51055c"
DEFAULT_OUTPUT_DIR = (
    Path(os.environ.get("USERPROFILE") or Path.home())
    / ".codex"
    / "communication-style"
)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_auth_config() -> AuthConfig:
    scopes = os.environ.get("COMM_STYLE_SCOPES", "User.Read,Mail.Read,Chat.Read").split(
        ","
    )
    return AuthConfig(
        client_id=_required_client_id(),
        tenant_id=os.environ.get("COMM_STYLE_TENANT_ID", "common"),
        scopes=[scope.strip() for scope in scopes if scope.strip()],
        mode=AuthMode(os.environ.get("COMM_STYLE_AUTH_MODE", "wam")),
        cache_namespace=os.environ.get(
            "MTG_AUTH_CACHE_NAMESPACE", DEFAULT_CACHE_NAMESPACE
        ),
        account_hint=os.environ.get("MTG_AUTH_ACCOUNT_HINT"),
        allow_broker=_env_bool("COMM_STYLE_ALLOW_BROKER", True),
    )


def default_output_dir() -> Path:
    return Path(
        os.environ.get("COMM_STYLE_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    ).expanduser()


def _required_client_id() -> str:
    client_id = os.environ.get("COMM_STYLE_CLIENT_ID", DEFAULT_CLIENT_ID).strip()
    if not client_id:
        raise RuntimeError(
            "COMM_STYLE_CLIENT_ID must be set to a real Entra public client application ID "
            "or omitted to use the shared Midtown app."
        )
    try:
        UUID(client_id)
    except ValueError as exc:
        raise RuntimeError(
            "COMM_STYLE_CLIENT_ID must be a valid Entra public client application ID UUID."
        ) from exc
    return client_id
