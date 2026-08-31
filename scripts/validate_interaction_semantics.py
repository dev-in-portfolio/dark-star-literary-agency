#!/usr/bin/env python3
"""Validate keyboard-oriented interaction semantics across public HTML pages."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".github", ".netlify", "node_modules", "docs", "data", "scripts"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang = ""
        self.main_ids: list[str] = []
        self.has_header = False
        self.has_footer = False
        self.has_primary_nav = False
        self.skip_link_before_header = False
        self._header_seen = False
        self.positive_tabindex: list[str] = []
        self.buttons_without_type = 0
        self.unsafe_blank_links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key.lower(): (value or "") for key, value in attrs}
        tag = tag.lower()

        if tag == "html":
            self.html_lang = attr.get("lang", "").strip().lower()
        elif tag == "header":
            self.has_header = True
            self._header_seen = True
        elif tag == "footer":
            self.has_footer = True
        elif tag == "main":
            self.main_ids.append(attr.get("id", ""))
        elif tag == "nav" and attr.get("aria-label", "").strip().lower() == "primary":
            self.has_primary_nav = True
        elif tag == "button" and "type" not in attr:
            self.buttons_without_type += 1

        classes = set(attr.get("class", "").split())
        if (
            tag == "a"
            and "skip-link" in classes
            and attr.get("href") == "#main"
            and not self._header_seen
        ):
            self.skip_link_before_header = True

        tabindex = attr.get("tabindex", "").strip()
        if tabindex and re.fullmatch(r"[+]?[1-9]\d*", tabindex):
            self.positive_tabindex.append(f"<{tag} tabindex={tabindex!r}>")

        if tag == "a" and attr.get("target", "").lower() == "_blank":
            rel = set(attr.get("rel", "").lower().split())
            if "noopener" not in rel:
                self.unsafe_blank_links.append(attr.get("href", ""))


def public_html_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*.html"):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        files.append(path)
    return sorted(files)


def is_redirect_page(text: str) -> bool:
    lowered = text.lower()
    return "http-equiv=\"refresh\"" in lowered or "http-equiv='refresh'" in lowered


def main() -> int:
    errors: list[str] = []
    checked = 0

    for path in public_html_files():
        relative = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{relative}: could not read HTML: {exc}")
            continue

        if is_redirect_page(text):
            continue

        parser = PageParser()
        try:
            parser.feed(text)
        except Exception as exc:  # HTMLParser errors are rare; preserve file context.
            errors.append(f"{relative}: parser error: {exc}")
            continue

        checked += 1
        if parser.html_lang != "en":
            errors.append(f"{relative}: expected <html lang=\"en\">")
        if not parser.skip_link_before_header:
            errors.append(f"{relative}: missing skip link to #main before the header")
        if parser.main_ids != ["main"]:
            errors.append(f"{relative}: expected exactly one <main id=\"main\">")
        if not parser.has_header:
            errors.append(f"{relative}: missing site header")
        if not parser.has_primary_nav:
            errors.append(f"{relative}: missing nav aria-label=\"Primary\"")
        if not parser.has_footer:
            errors.append(f"{relative}: missing site footer")
        if parser.positive_tabindex:
            errors.append(
                f"{relative}: positive tabindex values are not allowed: "
                + ", ".join(parser.positive_tabindex)
            )
        if parser.buttons_without_type:
            errors.append(
                f"{relative}: {parser.buttons_without_type} button element(s) lack an explicit type"
            )
        for href in parser.unsafe_blank_links:
            errors.append(
                f"{relative}: target=_blank link lacks rel=noopener: {href or '[empty href]'}"
            )

    if checked == 0:
        errors.append("No non-redirect public HTML pages were checked")

    if errors:
        print("Interaction semantics validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Validated interaction semantics for {checked} public HTML pages: "
        "language, skip link, landmarks, primary navigation, footer, tabindex, "
        "button types, and safe new-tab links."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
