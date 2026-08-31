#!/usr/bin/env python3
"""Validate the canonical Lulu & Ellie library master against generated public catalog output."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "library-master.json"


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    try:
        master = json.loads(MASTER.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Could not read data/library-master.json: {exc}")
        return 1

    if master.get("schema_version") != 1:
        fail("library master schema_version must be 1", errors)

    sources = master.get("storage_sources")
    if not isinstance(sources, list) or len(sources) != 7:
        fail("library master must define exactly seven storage sources", errors)
    else:
        repos = [item.get("repo") for item in sources if isinstance(item, dict)]
        expected = [f"dev-in-portfolio/l_e_storage{suffix}" for suffix in ("", "2", "3", "4", "5", "6", "7")]
        if sorted(repos) != sorted(expected):
            fail("library master storage source list does not match l_e_storage through l_e_storage7", errors)

    series_list = master.get("series")
    if not isinstance(series_list, list):
        fail("library master series must be a list", errors)
        series_list = []
    by_id = {item.get("id"): item for item in series_list if isinstance(item, dict)}

    required_ids = {"original-adventure","in-space","creature-rescue-club","mystery-tails","time-tails","go-to-camp"}
    if not required_ids.issubset(by_id):
        fail("library master is missing required story-series entries", errors)

    for sid, item in by_id.items():
        expected = item.get("expected_books")
        complete = item.get("complete_books")
        missing = item.get("missing_books")
        if not isinstance(expected, int) or expected <= 0:
            fail(f"{sid}: expected_books must be a positive integer", errors)
            continue
        if not isinstance(complete, list) or not isinstance(missing, list):
            fail(f"{sid}: complete_books and missing_books must be lists", errors)
            continue
        universe = set(range(1, expected + 1))
        cset, mset = set(complete), set(missing)
        if cset & mset:
            fail(f"{sid}: complete_books and missing_books overlap", errors)
        if cset | mset != universe:
            fail(f"{sid}: complete + missing books must exactly cover 1..{expected}", errors)

    original = by_id.get("original-adventure", {})
    books = original.get("books", [])
    if len(books) != 20:
        fail(f"original-adventure: expected 20 canonical book records, found {len(books)}", errors)
    else:
        numbers = [book.get("number") for book in books]
        if numbers != list(range(1, 21)):
            fail("original-adventure book numbers must be exactly 1 through 20 in order", errors)
        slugs = set()
        for book in books:
            if not isinstance(book.get("title"), str) or not book["title"].strip():
                fail(f"original-adventure Book {book.get('number')}: missing title", errors)
            slug = book.get("slug")
            if not isinstance(slug, str) or not slug.strip():
                fail(f"original-adventure Book {book.get('number')}: missing slug", errors)
                continue
            if slug in slugs:
                fail(f"original-adventure duplicate slug: {slug}", errors)
            slugs.add(slug)
            page = ROOT / "books" / f"{slug}.html"
            if not page.is_file():
                fail(f"missing generated canonical book page: {page.relative_to(ROOT)}", errors)

    series_page = ROOT / "series" / "lulu-and-ellie-adventures.html"
    if not series_page.is_file():
        fail("missing Original Adventure series page", errors)
    else:
        text = series_page.read_text(encoding="utf-8")
        for number in range(1, 21):
            if f"Book {number}</span>" not in text:
                fail(f"Original Adventure series page missing Book {number} card", errors)

    archive_page = ROOT / "lulu-ellie" / "original-adventure" / "index.html"
    if not archive_page.is_file():
        fail("missing Original Adventure archive page", errors)
    else:
        text = archive_page.read_text(encoding="utf-8")
        stale = ("Volumes 11–20", "Archive Volume 11", "ten named storybooks")
        for phrase in stale:
            if phrase in text:
                fail(f"Original Adventure archive still contains stale wording: {phrase}", errors)
        if "Original Adventure Books 1–20" not in text and "Books 1–20" not in text:
            fail("Original Adventure archive does not present the complete 20-book sequence", errors)

    library = ROOT / "library.html"
    if not library.is_file():
        fail("missing Library page", errors)
    else:
        text = library.read_text(encoding="utf-8")
        for phrase in ("Lulu &amp; Ellie Time Tails", "Books 1–20", "Lulu &amp; Ellie and the Keeper Ring"):
            if phrase not in text:
                fail(f"Library missing reconciled catalog content: {phrase}", errors)

    mystery = ROOT / "series" / "mystery-tails.html"
    if not mystery.is_file():
        fail("missing Mystery Tails page", errors)
    else:
        text = mystery.read_text(encoding="utf-8")
        for title in (
            "The Case of the Missing Moon Biscuit",
            "The Secret of the Whispering Mailbox",
            "The Pawprints That Walked Backward",
            "The Haunted Treat Truck",
            "The Lighthouse That Barked",
        ):
            if title not in text:
                fail(f"Mystery Tails page missing source-confirmed title: {title}", errors)
        for stale in ("Missing Mooncake", "Lighthouse That Blinked Twice", "Pawprints in the Pumpkin Patch"):
            if stale in text:
                fail(f"Mystery Tails page still exposes stale concept title: {stale}", errors)

    if not (ROOT / "series" / "time-tails.html").is_file():
        fail("Time Tails is missing from the public series architecture", errors)

    for page in ROOT.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        stale_purchase_targets = (
            "series/lulu-and-ellie-adventures.html#purchase",
            "../series/lulu-and-ellie-adventures.html#purchase",
        )
        for stale_target in stale_purchase_targets:
            if stale_target in text:
                fail(f"{page.relative_to(ROOT)}: stale cross-page purchase fragment remains: {stale_target}", errors)
        if "http-equiv=\"refresh\"" in text.lower() or "http-equiv='refresh'" in text.lower():
            continue
        if "favicon.svg" not in text:
            fail(f"{page.relative_to(ROOT)}: missing favicon link", errors)
        if "accessibility.css" not in text:
            fail(f"{page.relative_to(ROOT)}: missing accessibility stylesheet", errors)

    if errors:
        print("Library master validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validated seven storage sources, canonical Original Adventure Books 1–20, Mystery Tails reconciliation, Time Tails architecture, and cross-site catalog invariants.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
