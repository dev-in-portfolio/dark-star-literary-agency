#!/usr/bin/env python3
"""Validate the Dark Star static site without third-party dependencies."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".github", "node_modules"}
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "sms", "data", "javascript"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str, str]] = []
        self.ids: list[str] = []
        self.errors: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False
        self.h1_count = 0
        self.meta_description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        tag = tag.lower()

        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1

        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)

        if tag == "meta" and values.get("name", "").lower() == "description":
            self.meta_description = values.get("content", "").strip()

        for attribute in ("href", "src", "poster"):
            value = values.get(attribute, "").strip()
            if value:
                self.references.append((tag, attribute, value))

        if tag == "img":
            has_alt = "alt" in values
            is_decorative = values.get("role") == "presentation" or values.get("aria-hidden") == "true"
            if not has_alt or (not values.get("alt", "").strip() and not is_decorative):
                self.errors.append("image is missing useful alt text")

        if tag == "a" and values.get("href") == "#" and values.get("aria-disabled") != "true":
            self.errors.append('anchor uses href="#" without aria-disabled="true"')

        if tag == "video" and "autoplay" in values:
            if "muted" not in values:
                self.errors.append("autoplay video is not muted")
            if "playsinline" not in values:
                self.errors.append("autoplay video is missing playsinline")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


def html_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.html")
        if not any(part in IGNORED_PARTS for part in path.parts)
    )


def resolve_local_reference(page: Path, value: str) -> Path | None:
    if value.startswith("#"):
        return None

    parsed = urlsplit(value)
    if parsed.scheme.lower() in EXTERNAL_SCHEMES or parsed.netloc:
        return None

    clean_path = unquote(parsed.path)
    if not clean_path:
        return None

    target = ROOT / clean_path.lstrip("/") if clean_path.startswith("/") else page.parent / clean_path
    target = target.resolve()

    try:
        target.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"reference escapes repository root: {value}") from exc

    if clean_path.endswith("/") or target.is_dir():
        target = target / "index.html"

    return target


def validate_html() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    titles: Counter[str] = Counter()

    pages = html_files()
    if not pages:
        errors.append("no HTML files found")
        return errors, warnings

    for page in pages:
        relative = page.relative_to(ROOT)
        parser = PageParser()
        try:
            parser.feed(page.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{relative}: could not read/parse file: {exc}")
            continue

        if not parser.title:
            errors.append(f"{relative}: missing <title>")
        else:
            titles[parser.title] += 1

        if not parser.meta_description:
            errors.append(f"{relative}: missing meta description")

        if parser.h1_count != 1:
            errors.append(f"{relative}: expected exactly one <h1>, found {parser.h1_count}")

        for message in parser.errors:
            errors.append(f"{relative}: {message}")

        duplicate_ids = sorted(name for name, count in Counter(parser.ids).items() if count > 1)
        if duplicate_ids:
            errors.append(f"{relative}: duplicate IDs: {', '.join(duplicate_ids)}")

        for tag, attribute, value in parser.references:
            if value.startswith("http://"):
                errors.append(f"{relative}: insecure external URL in {tag}[{attribute}]: {value}")
                continue
            try:
                target = resolve_local_reference(page, value)
            except ValueError as exc:
                errors.append(f"{relative}: {exc}")
                continue
            if target is not None and not target.exists():
                errors.append(f"{relative}: missing local target for {tag}[{attribute}]={value}")

    for title, count in sorted(titles.items()):
        if count > 1:
            warnings.append(f'duplicate page title used {count} times: "{title}"')

    return errors, warnings


def validate_original_adventure_media() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    base = ROOT / "assets" / "lulu-ellie" / "original-adventure"

    for number in range(1, 21):
        folder = base / f"book-{number}"
        if not folder.is_dir():
            errors.append(f"missing media folder: {folder.relative_to(ROOT)}")
            continue

        covers = [path for path in folder.glob("front-cover.*") if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
        if len(covers) != 1:
            errors.append(
                f"{folder.relative_to(ROOT)}: expected one front cover, found {len(covers)}"
            )

        animation = folder / "animated-cover.mp4"
        if not animation.is_file():
            errors.append(f"missing animation: {animation.relative_to(ROOT)}")
        elif animation.stat().st_size > 12 * 1024 * 1024:
            warnings.append(
                f"large animation ({animation.stat().st_size / 1024 / 1024:.1f} MiB): {animation.relative_to(ROOT)}"
            )

        feature = folder / "feature-page.png"
        if number >= 2 and not feature.is_file():
            errors.append(f"missing feature page: {feature.relative_to(ROOT)}")

    return errors, warnings


def main() -> int:
    errors, warnings = validate_html()
    media_errors, media_warnings = validate_original_adventure_media()
    errors.extend(media_errors)
    warnings.extend(media_warnings)

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        print("\nSite validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(html_files())} HTML pages and all 20 Original Adventure media folders.")
    if warnings:
        print(f"Completed with {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
