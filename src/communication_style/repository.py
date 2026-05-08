from __future__ import annotations

import time

from communication_style.models import CommunicationSample
from communication_style.text import html_to_text, normalize_text


class CommunicationRepository:
    def __init__(self, graph_client) -> None:
        self.graph_client = graph_client
        self.progress = None

    def current_user(self) -> dict:
        return self.graph_client.get(
            "/me", {"$select": "id,userPrincipalName,displayName"}
        )

    def chat_members(self, chat_id: str) -> list[str]:
        members = []
        try:
            payload = self.graph_client.get(
                f"/me/chats/{chat_id}/members", {"$top": 50}
            )
            for row in payload.get("value", []):
                display_name = row.get("displayName")
                email = row.get("email")
                user_id = row.get("userId")
                value = " ".join(
                    part for part in [display_name, email, user_id] if part
                )
                if value:
                    members.append(value)
        except Exception as exc:
            if self.progress:
                self.progress(f"skipped members {chat_id}", 0, str(exc))
        return members

    def sent_mail(self, *, limit: int | None = 250) -> list[CommunicationSample]:
        params = {
            "$top": 100 if limit is None else min(limit, 100),
            "$orderby": "sentDateTime desc",
            "$select": "id,sentDateTime,conversationId,subject,body,bodyPreview,toRecipients,ccRecipients,bccRecipients",
        }
        samples: list[CommunicationSample] = []
        for raw in self._iter_values(
            "/me/mailFolders/sentitems/messages",
            params=params,
            limit=limit,
            label="sent mail",
        ):
            body = raw.get("body") or {}
            text = html_to_text(body.get("content")) or normalize_text(
                raw.get("bodyPreview")
            )
            if text:
                samples.append(
                    CommunicationSample(
                        source="sent-mail",
                        id=raw.get("id", ""),
                        created=raw.get("sentDateTime"),
                        conversation_id=raw.get("conversationId"),
                        subject=raw.get("subject"),
                        text=text,
                        participants=_mail_participants(raw),
                    )
                )
        return samples

    def authored_chat_messages(
        self,
        *,
        user_id: str,
        chat_limit: int | None = 50,
        message_limit: int | None = 500,
    ) -> list[CommunicationSample]:
        chats = list(
            self._iter_values(
                "/me/chats", {"$top": 50}, limit=chat_limit, label="chats"
            )
        )
        samples: list[CommunicationSample] = []
        for chat in chats:
            if message_limit is not None and len(samples) >= message_limit:
                break
            chat_id = chat.get("id")
            if not chat_id:
                continue
            remaining = None if message_limit is None else message_limit - len(samples)
            try:
                messages = self._iter_values(
                    f"/me/chats/{chat_id}/messages",
                    {"$top": 50 if remaining is None else min(remaining, 50)},
                    limit=remaining,
                    label="chat messages",
                )
                for raw in messages:
                    if message_limit is not None and len(samples) >= message_limit:
                        break
                    sender = ((raw.get("from") or {}).get("user") or {}).get("id")
                    if sender != user_id:
                        continue
                    body = raw.get("body") or {}
                    text = html_to_text(body.get("content"))
                    if text:
                        samples.append(
                            CommunicationSample(
                                source="teams-chat",
                                id=raw.get("id", ""),
                                created=raw.get("createdDateTime"),
                                conversation_id=chat_id,
                                subject=chat.get("topic"),
                                text=text,
                            )
                        )
            except Exception as exc:
                if self.progress:
                    self.progress(f"skipped chat {chat_id}", 0, str(exc))
        return samples

    def _iter_values(
        self,
        path: str,
        params: dict | None = None,
        *,
        limit: int | None = None,
        label: str = "items",
    ):
        count = 0
        page = 0
        next_url: str | None = f"{self.graph_client.BASE_URL}{path}"
        request_params = params
        while next_url:
            payload = self._get_page(next_url, request_params)
            page += 1
            for row in payload.get("value", []):
                if limit is not None and count >= limit:
                    return
                yield row
                count += 1
            if self.progress:
                self.progress(label, page, count)
            next_url = payload.get("@odata.nextLink")
            request_params = None

    def _get_page(self, url: str, params: dict | None) -> dict:
        last_error: Exception | None = None
        for attempt in range(5):
            try:
                return self.graph_client._request_with_retry(
                    "GET", url, params=params
                ).json()
            except Exception as exc:
                last_error = exc
                if attempt == 4:
                    break
                time.sleep(2 * (attempt + 1))
        raise last_error or RuntimeError("Graph page request failed.")


def _mail_participants(raw: dict) -> list[str]:
    values = []
    for key in ("toRecipients", "ccRecipients", "bccRecipients"):
        for recipient in raw.get(key, []) or []:
            address = recipient.get("emailAddress") or {}
            value = " ".join(
                part for part in [address.get("name"), address.get("address")] if part
            )
            if value:
                values.append(value)
    return values
