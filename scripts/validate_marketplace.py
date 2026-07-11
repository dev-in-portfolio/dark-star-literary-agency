#!/usr/bin/env python3
"""Validate evidence-based marketplace wording against the marketplace registry."""

from __future__ import annotations

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BOOKS_DIR = ROOT / "books"
SERIES_PAGE = ROOT / "series" / "lulu-and-ellie-adventures.html"
LIBRARY_PAGE = ROOT / "library.html"
REGISTRY_PATH = ROOT / "data" / "marketplace-records.json"

FORBIDDEN_PHRASES = (
    "Paperback available",
    "Buy on Amazon",
    "Where to Purchase",
    "Paperback · $",
)

PRICE_PATTERN = re.compile(r"\$\d+(?:\.\d{2})?")
ASIN_PATTERN = re.compile(r"^[A-Z0-9]{10}$")
ALLOWED_STATUSES = {
    "link-on-file-current-state-unverified",
    "no-active-link-on-file-current-state-unverified",
    "manually-verified-current",
}


def load_registry() -> tuple[list[dict[str, object]], list[str]]:
    errors: list[str] = []

    if not REGISTRY_PATH.is_file():
        return [], [f"missing marketplace registry: {REGISTRY_PATH.relative_to(ROOT)}"]

    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [], [f"{REGISTRY_PATH.relative_to(ROOT)}: invalid JSON: {exc}"]

    if registry.get("schema_version") != 1:
        errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: unsupported schema version")

    if registry.get("marketplace") != "Amazon US":
        errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: marketplace must be Amazon US")

    if not isinstance(registry.get("last_automated_audit"), str):
        errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: missing last automated audit date")

    records = registry.get("records")
    if not isinstance(records, list):
        return [], errors + [f"{REGISTRY_PATH.relative_to(ROOT)}: records must be a list"]

    if len(records) != 10:
        errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: expected 10 records, found {len(records)}")

    numbers: list[int] = []
    filenames: list[str] = []
    asins: list[str] = []

    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: record {index} must be an object")
            continue

        number = record.get("book_number")
        filename = record.get("filename")
        title = record.get("title")
        asin = record.get("asin")
        url = record.get("url")
        status = record.get("status")

        if not isinstance(number, int) or not 1 <= number <= 10:
            errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: record {index} has invalid book number")
        else:
            numbers.append(number)

        if not isinstance(filename, str) or not filename.endswith(".html"):
            errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: Book {number} has invalid filename")
        else:
            filenames.append(filename)

        if not isinstance(title, str) or not title.strip():
            errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: Book {number} is missing a title")

        if status not in ALLOWED_STATUSES:
            errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: Book {number} has invalid status {status}")

        if number == 6:
            if asin is not None or url is not None:
                errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: Book 6 must not have an active ASIN or URL")
            if status != "no-active-link-on-file-current-state-unverified":
                errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: Book 6 must use the no-link status")
        else:
            if not isinstance(asin, str) or not ASIN_PATTERN.fullmatch(asin):
                errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: Book {number} has invalid ASIN")
            else:
                asins.append(asin)
                expected_url = f"https://www.amazon.com/dp/{asin}"
                if url != expected_url:
                    errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: Book {number} URL does not match its ASIN")

    if sorted(numbers) != list(range(1, 11)):
        errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: book numbers must be exactly 1 through 10")
    if len(set(filenames)) != len(filenames):
        errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: duplicate filenames")
    if len(set(asins)) != len(asins):
        errors.append(f"{REGISTRY_PATH.relative_to(ROOT)}: duplicate ASINs")

    return records, errors


def validate_book(record: dict[str, object]) -> list[str]:
    errors: list[str] = []
    number = int(record["book_number"])
    filename = str(record["filename"])
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

    expected_url = str(record["url"])
    if expected_url not in text:
        errors.append(f"{relative}: missing registry marketplace link {expected_url}")

    return errors


def validate_series_page(records: list[dict[str, object]]) -> list[str]:
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

    for record in records:
        if record.get("url") is None:
            continue
        expected_url = str(record["url"])
        if expected_url not in text:
            errors.append(
                f"{relative}: missing recorded Book {record.get('book_number')} marketplace link {expected_url}"
            )

    return errors


def validate_library_page() -> list[str]:
    errors: list[str] = []
    relative = LIBRARY_PAGE.relative_to(ROOT)

    if not LIBRARY_PAGE.is_file():
        return [f"missing Library page: {relative}"]

    text = LIBRARY_PAGE.read_text(encoding="utf-8")
    requirements = (
        '<link rel="stylesheet" href="accessibility.css">',
        '<span class="status-badge">Growing library</span>',
        "Recorded Amazon links are shown on canonical storybook pages.",
        "Current price, format, and availability must be confirmed on Amazon.",
    )
    for phrase in requirements:
        if phrase not in text:
            errors.append(f"{relative}: missing current Library wording: {phrase}")

    stale_phrases = (
        '<span class="status-badge">Coming soon</span>',
        "Live paperback purchase links are shown",
    )
    for phrase in stale_phrases:
        if phrase in text:
            errors.append(f"{relative}: contains stale Library wording: {phrase}")

    return errors


def main() -> int:
    records, errors = load_registry()
    for record in records:
        if isinstance(record, dict):
            errors.extend(validate_book(record))
    errors.extend(validate_series_page(records))
    errors.extend(validate_library_page())

    if errors:
        print("Marketplace registry, page, and Library validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Validated the marketplace registry, evidence-based wording for canonical Books 1–10, "
        "the series page, and the live Library page."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
