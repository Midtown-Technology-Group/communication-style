from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class CommunicationSample:
    source: str
    id: str
    created: str | None
    conversation_id: str | None
    subject: str | None
    text: str
    participants: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CollectionSummary:
    collected_at: str
    user_id: str
    user_principal_name: str | None
    mail_samples: int
    chat_samples: int
    output_path: str

    @classmethod
    def now(
        cls,
        *,
        user_id: str,
        user_principal_name: str | None,
        mail_samples: int,
        chat_samples: int,
        output_path: str,
    ) -> "CollectionSummary":
        return cls(
            collected_at=datetime.now().isoformat(timespec="seconds"),
            user_id=user_id,
            user_principal_name=user_principal_name,
            mail_samples=mail_samples,
            chat_samples=chat_samples,
            output_path=output_path,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
