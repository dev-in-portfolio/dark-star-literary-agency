#!/usr/bin/env python3
"""Validate evidence-based marketplace wording on canonical Lulu & Ellie pages."""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BOOKS_DIR = ROOT / "books"
SERIES_PAGE = ROOT / "series" / "lulu-and-ellie-adventures.html"

BOOKS = [
    (1, "lulu-and-ellie-and-the-secret-of-blackwater-bay.html", "B0H351G4MG"),
    (2, "lulu-and-ellie-and-the-lost-valley-of-thunder.html", "B0H35QR6C6"),
    (3, "lulu-and-ellie-and-the-clockwork-forest.html", "B0H32KRFDF"),
    (4, "lulu-and-ellie-and-the-moonlit-circus.html", "B0H36D98XX"),
    (5, "lulu-and-ellie-and-the-snow-dragons-bell.html", "B0H33K2RDN"),
    (6, "lulu-and-ellie-and-the-mushroom-moon-maze.html", None),
    (7, "lulu-and-ellie-and-the-lanterns-of-the-deep.html", "B0H3351L1P"),
    (8, "lulu-and-ellie-and-the-book-that-lost-its-ending.html", "B0H35JL3PQ"),
    (9, "lulu-and-ellie-and-the-island-that-drifted-away.html", "B0H33NFZYB"),
    (10, "lulu-and-ellie-and-the-star-map-of-everywhere.html", "B0H33RFB7T"),
]

FORBIDDEN_PHRASES = (
    "Paperback available",
    "Buy on Amazon",
    "Where to Purchase",
    "Paperback · $",
)

PRICE_PATTERN = re.compile(r"\$\d+(?:\.\d{2})?")


def validate_book(number: int, filename: str, asin: str | None) -> list[str]:
    errors: list[str] = []
    path = BOOKS_DIR / filename
    relative = path.relative_to(ROOT)

    if not path.is_file():
        return [f"missing canonical marketplace page: {relative}"]

    text = path.read_text(encoding="utf-8")

    for phrase in FORBIDDEN_PHRASES:
        if phrase in text:
            errors.append(f"{relative}: contains unsupported marketplace phrase: {phrase}")

    if PRICE_PATTERN.search(text):
        errors.append(f"{relative}: contains a fixed marketplace price")

    if 'id="marketplace"' not in text:
        errors.append(f"{relative}: missing marketplace section")

    if number == 6:
        required = (
            "No active Amazon link",
            "Current status unverified",
            "No active Amazon link on file",
        )
        for phrase in required:
            if phrase not in text:
                errors.append(f"{relative}: missing Book 6 no-link wording: {phrase}")
        if "amazon.com/dp/" in text:
            errors.append(f"{relative}: Book 6 must not expose an active Amazon product link")
        return errors

    required = (
        "Amazon link on file",
        "Current status unverified",
        "Current price and availability unverified",
        "Check Amazon",
    )
    for phrase in required:
        if phrase not in text:
            errors.append(f"{relative}: missing evidence-based marketplace wording: {phrase}")

    expected_url = f"https://www.amazon.com/dp/{asin}"
    if expected_url not in text:
        errors.append(f"{relative}: missing recorded ASIN link {asin}")

    return errors


def validate_series_page() -> list[str]:
    errors: list[str] = []
    relative = SERIES_PAGE.relative_to(ROOT)

    if not SERIES_PAGE.is_file():
        return [f"missing series marketplace page: {relative}"]

    text = SERIES_PAGE.read_text(encoding="utf-8")
    if PRICE_PATTERN.search(text):
        errors.append(f"{relative}: contains a fixed marketplace price")
    if "Confirmed public paperback links" in text:
        errors.append(f"{relative}: still claims marketplace links are currently confirmed")
    if "Amazon link on file" not in text:
        errors.append(f"{relative}: missing evidence-based marketplace wording")

    for number, _, asin in BOOKS:
        if number == 6:
            continue
        expected_url = f"https://www.amazon.com/dp/{asin}"
        if expected_url not in text:
            errors.append(f"{relative}: missing recorded Book {number} ASIN link {asin}")

    return errors


def main() -> int:
    errors: list[str] = []
    for record in BOOKS:
        errors.extend(validate_book(*record))
    errors.extend(validate_series_page())

    if errors:
        print("Marketplace validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validated evidence-based marketplace wording for canonical Books 1–10 and the series page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
