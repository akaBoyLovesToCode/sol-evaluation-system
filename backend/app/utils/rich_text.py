"""Utilities for safely storing and rendering limited rich text."""

from __future__ import annotations

from html import escape
from html.parser import HTMLParser

ALLOWED_TAGS = {
    "b",
    "br",
    "col",
    "colgroup",
    "div",
    "em",
    "i",
    "li",
    "ol",
    "p",
    "strong",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "u",
    "ul",
}
ALLOWED_ATTRIBUTES = {
    "col": {"width"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan"},
}
BLOCKED_CONTENT_TAGS = {"iframe", "object", "script", "style", "svg"}
VOID_TAGS = {"br", "col"}


class _RichTextSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.blocked_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in BLOCKED_CONTENT_TAGS:
            self.blocked_depth += 1
            return
        if self.blocked_depth or tag not in ALLOWED_TAGS:
            return

        safe_attrs: list[str] = []
        for name, value in attrs:
            name = name.lower()
            if name not in ALLOWED_ATTRIBUTES.get(tag, set()) or value is None:
                continue
            if not value.isdigit():
                continue
            number = int(value)
            if name in {"colspan", "rowspan"} and not 1 <= number <= 100:
                continue
            if tag == "col" and name == "width" and not 40 <= number <= 5000:
                continue
            safe_attrs.append(f'{name}="{escape(value, quote=True)}"')

        attr_text = f" {' '.join(safe_attrs)}" if safe_attrs else ""
        self.parts.append(f"<{tag}{attr_text}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in BLOCKED_CONTENT_TAGS:
            return
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in BLOCKED_CONTENT_TAGS:
            self.blocked_depth = max(self.blocked_depth - 1, 0)
            return
        if self.blocked_depth or tag not in ALLOWED_TAGS or tag in VOID_TAGS:
            return
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self.blocked_depth:
            self.parts.append(escape(data))


def sanitize_rich_text(value: object) -> str:
    """Return rich text containing only the supported formatting tags."""
    if not isinstance(value, str) or not value.strip():
        return ""

    sanitizer = _RichTextSanitizer()
    sanitizer.feed(value)
    sanitizer.close()
    return "".join(sanitizer.parts).strip()
