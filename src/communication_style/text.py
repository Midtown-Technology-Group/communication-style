from __future__ import annotations

import re
from html import unescape

HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
REPLY_MARKER_RE = re.compile(r"(?im)^(from:|sent:|to:|subject:|on .+ wrote:).*$")
SIGNATURE_MARKERS = (
    "\n-- ",
    "\nthanks,",
    "\nthank you,",
    "\nbest,",
    "\nregards,",
)


def html_to_text(value: str | None) -> str:
    if not value:
        return ""
    text = re.sub(r"(?i)<p[^>]*>", "\n", value)
    text = re.sub(r"(?i)<div[^>]*>", "\n", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p\s*>", "\n", text)
    text = re.sub(r"(?i)</div\s*>", "\n", text)
    text = HTML_TAG_RE.sub(" ", text)
    return normalize_text(unescape(text))


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    text = value.replace("\r\n", "\n").replace("\r", "\n")
    text = _strip_reply_chain(text)
    text = _strip_signature(text)
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def _strip_reply_chain(text: str) -> str:
    match = REPLY_MARKER_RE.search(text)
    if match:
        return text[: match.start()]
    return text


def _strip_signature(text: str) -> str:
    lowered = text.lower()
    for marker in SIGNATURE_MARKERS:
        index = lowered.find(marker)
        if index > 10:
            return text[:index]
    return text
