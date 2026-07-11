#!/usr/bin/env python3
"""Validate the Dark Star static site without third-party dependencies."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".github", "node_modules"}
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "sms", "data", "javascript"}

CANONICAL_BOOKS = [
    (1, "lulu-and-ellie-and-the-secret-of-blackwater-bay.html", None, "lulu-and-ellie-and-the-lost-valley-of-thunder.html"),
    (2, "lulu-and-ellie-and-the-lost-valley-of-thunder.html", "lulu-and-ellie-and-the-secret-of-blackwater-bay.html", "lulu-and-ellie-and-the-clockwork-forest.html"),
    (3, "lulu-and-ellie-and-the-clockwork-forest.html", "lulu-and-ellie-and-the-lost-valley-of-thunder.html", "lulu-and-ellie-and-the-moonlit-circus.html"),
    (4, "lulu-and-ellie-and-the-moonlit-circus.html", "lulu-and-ellie-and-the-clockwork-forest.html", "lulu-and-ellie-and-the-snow-dragons-bell.html"),
    (5, "lulu-and-ellie-and-the-snow-dragons-bell.html", "lulu-and-ellie-and-the-moonlit-circus.html", "lulu-and-ellie-and-the-mushroom-moon-maze.html"),
    (6, "lulu-and-ellie-and-the-mushroom-moon-maze.html", "lulu-and-ellie-and-the-snow-dragons-bell.html", "lulu-and-ellie-and-the-lanterns-of-the-deep.html"),
    (7, "lulu-and-ellie-and-the-lanterns-of-the-deep.html", "lulu-and-ellie-and-the-mushroom-moon-maze.html", "lulu-and-ellie-and-the-book-that-lost-its-ending.html"),
    (8, "lulu-and-ellie-and-the-book-that-lost-its-ending.html", "lulu-and-ellie-and-the-lanterns-of-the-deep.html", "lulu-and-ellie-and-the-island-that-drifted-away.html"),
    (9, "lulu-and-ellie-and-the-island-that-drifted-away.html", "lulu-and-ellie-and-the-book-that-lost-its-ending.html", "lulu-and-ellie-and-the-star-map-of-everywhere.html"),
    (10, "lulu-and-ellie-and-the-star-map-of-everywhere.html", "lulu-and-ellie-and-the-island-that-drifted-away.html", None),
]


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
            errors.append(f"{folder.relative_to(ROOT)}: expected one front cover, found {len(covers)}")

        animation = folder / "animated-cover.mp4"
        if not animation.is_file():
            errors.append(f"missing animation: {animation.relative_to(ROOT)}")
        elif animation.stat().st_size > 12 * 1024 * 1024:
            warnings.append(f"large animation ({animation.stat().st_size / 1024 / 1024:.1f} MiB): {animation.relative_to(ROOT)}")

        feature = folder / "feature-page.png"
        if number >= 2 and not feature.is_file():
            errors.append(f"missing feature page: {feature.relative_to(ROOT)}")

    return errors, warnings


def validate_canonical_book_pages() -> list[str]:
    errors: list[str] = []
    books_dir = ROOT / "books"

    for number, filename, previous_file, next_file in CANONICAL_BOOKS:
        page = books_dir / filename
        if not page.is_file():
            errors.append(f"missing canonical book page: {page.relative_to(ROOT)}")
            continue

        text = page.read_text(encoding="utf-8")
        if f"<span>Book {number}</span>" not in text:
            errors.append(f"{page.relative_to(ROOT)}: canonical Book {number} label is missing")
        if f"original-adventure/book-{number}/" not in text:
            errors.append(f"{page.relative_to(ROOT)}: media is not mapped to book-{number}")
        if previous_file and previous_file not in text:
            errors.append(f"{page.relative_to(ROOT)}: previous-book link should point to {previous_file}")
        if next_file and next_file not in text:
            errors.append(f"{page.relative_to(ROOT)}: next-book link should point to {next_file}")

    series_page = ROOT / "series" / "lulu-and-ellie-adventures.html"
    if not series_page.is_file():
        errors.append("missing Original Adventure series page")
    else:
        series_text = series_page.read_text(encoding="utf-8")
        for number, filename, _, _ in CANONICAL_BOOKS:
            if f'<span class="book-number">Book {number}</span>' not in series_text:
                errors.append(f"{series_page.relative_to(ROOT)}: missing canonical Book {number} card")
            if filename not in series_text:
                errors.append(f"{series_page.relative_to(ROOT)}: missing link to {filename}")

    return errors


def validate_companion_catalog() -> list[str]:
    errors: list[str] = []
    catalog_path = ROOT / "data" / "companion-catalog.json"
    page_path = ROOT / "companion-library.html"
    script_path = ROOT / "companion-library.js"

    for required in (catalog_path, page_path, script_path):
        if not required.is_file():
            errors.append(f"missing companion catalog file: {required.relative_to(ROOT)}")

    if not catalog_path.is_file():
        return errors

    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{catalog_path.relative_to(ROOT)}: invalid catalog JSON: {exc}")
        return errors

    collections = catalog.get("collections")
    if not isinstance(collections, list):
        errors.append(f"{catalog_path.relative_to(ROOT)}: collections must be a list")
        return errors

    if len(collections) != 12:
        errors.append(f"{catalog_path.relative_to(ROOT)}: expected 12 collections, found {len(collections)}")

    titles: list[str] = []
    for collection in collections:
        name = collection.get("collection")
        items = collection.get("items")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{catalog_path.relative_to(ROOT)}: collection is missing a public name")
        if not isinstance(items, list) or not items:
            errors.append(f"{catalog_path.relative_to(ROOT)}: {name or 'unnamed collection'} has no items")
            continue
        for item in items:
            title = item.get("title")
            pages = item.get("pages")
            if not isinstance(title, str) or not title.strip():
                errors.append(f"{catalog_path.relative_to(ROOT)}: item is missing a title")
            else:
                titles.append(title.strip())
            if not isinstance(pages, int) or pages <= 0:
                errors.append(f"{catalog_path.relative_to(ROOT)}: {title or 'untitled item'} has an invalid page count")

    if len(titles) != 44:
        errors.append(f"{catalog_path.relative_to(ROOT)}: expected 44 titles, found {len(titles)}")

    duplicates = sorted(title for title, count in Counter(titles).items() if count > 1)
    if duplicates:
        errors.append(f"{catalog_path.relative_to(ROOT)}: duplicate titles: {', '.join(duplicates)}")

    return errors


def main() -> int:
    errors, warnings = validate_html()
    media_errors, media_warnings = validate_original_adventure_media()
    errors.extend(media_errors)
    warnings.extend(media_warnings)
    errors.extend(validate_canonical_book_pages())
    errors.extend(validate_companion_catalog())

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        print("\nSite validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Validated {len(html_files())} HTML pages, all 20 Original Adventure media folders, "
        "the canonical Books 1-10 sequence, and 44 companion catalog titles."
    )
    if warnings:
        print(f"Completed with {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
