#!/usr/bin/env python3
"""Reconcile the public companion catalog with the creator-supplied PDF manifest."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import csv
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "companion-catalog.json"
MANIFEST_PATH = ROOT / "data" / "companion-source-manifest.csv"
REQUIRED_COLUMNS = {
    "id",
    "collection",
    "title",
    "source_package",
    "source_file",
    "pages",
    "sha256",
    "quality_status",
    "marketplace_status",
    "last_reviewed",
}
ALLOWED_QUALITY = {
    "polished-preview",
    "final-qa-pending",
    "revision-pass-pending",
    "character-continuity-review",
}


def load_catalog() -> dict[tuple[str, str], int]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    records: dict[tuple[str, str], int] = {}
    for collection in catalog.get("collections", []):
        collection_name = collection.get("collection")
        for item in collection.get("items", []):
            title = item.get("title")
            pages = item.get("pages")
            if not isinstance(collection_name, str) or not isinstance(title, str) or not isinstance(pages, int):
                raise ValueError("catalog contains an invalid collection, title, or page count")
            records[(collection_name.strip(), title.strip())] = pages
    return records


def load_manifest() -> tuple[list[dict[str, str]], list[str]]:
    errors: list[str] = []
    with MANIFEST_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - columns)
        if missing:
            return [], [f"manifest is missing columns: {', '.join(missing)}"]
        rows = list(reader)

    if len(rows) != 44:
        errors.append(f"expected 44 manifest rows, found {len(rows)}")
    return rows, errors


def validate() -> list[str]:
    errors: list[str] = []
    if not CATALOG_PATH.is_file():
        return [f"missing catalog: {CATALOG_PATH.relative_to(ROOT)}"]
    if not MANIFEST_PATH.is_file():
        return [f"missing manifest: {MANIFEST_PATH.relative_to(ROOT)}"]

    try:
        catalog_records = load_catalog()
        rows, row_errors = load_manifest()
        errors.extend(row_errors)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, csv.Error, ValueError) as exc:
        return [f"could not read companion source data: {exc}"]

    ids: list[str] = []
    manifest_records: dict[tuple[str, str], int] = {}

    for row_number, row in enumerate(rows, start=2):
        item_id = row["id"].strip()
        collection = row["collection"].strip()
        title = row["title"].strip()
        source_package = row["source_package"].strip()
        source_file = row["source_file"].strip()
        sha256 = row["sha256"].strip()
        quality_status = row["quality_status"].strip()
        marketplace_status = row["marketplace_status"].strip()
        last_reviewed = row["last_reviewed"].strip()

        if not item_id:
            errors.append(f"row {row_number}: missing id")
        else:
            ids.append(item_id)

        for field_name, value in (
            ("collection", collection),
            ("title", title),
            ("source_package", source_package),
            ("source_file", source_file),
            ("marketplace_status", marketplace_status),
        ):
            if not value:
                errors.append(f"row {row_number}: missing {field_name}")

        try:
            pages = int(row["pages"])
        except (TypeError, ValueError):
            pages = 0
        if pages <= 0:
            errors.append(f"row {row_number}: invalid page count")

        if not re.fullmatch(r"[0-9a-f]{64}", sha256):
            errors.append(f"row {row_number}: invalid SHA-256")
        if quality_status not in ALLOWED_QUALITY:
            errors.append(f"row {row_number}: invalid quality status {quality_status!r}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", last_reviewed):
            errors.append(f"row {row_number}: invalid review date")

        key = (collection, title)
        if key in manifest_records:
            errors.append(f"row {row_number}: duplicate collection/title record")
        manifest_records[key] = pages

    duplicate_ids = sorted(item_id for item_id, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        errors.append(f"duplicate manifest ids: {', '.join(duplicate_ids)}")

    if len(catalog_records) != 44:
        errors.append(f"expected 44 catalog records, found {len(catalog_records)}")

    for key, catalog_pages in catalog_records.items():
        manifest_pages = manifest_records.get(key)
        if manifest_pages is None:
            errors.append(f"catalog item missing from manifest: {key[0]} / {key[1]}")
        elif manifest_pages != catalog_pages:
            errors.append(
                f"page-count mismatch for {key[1]}: catalog {catalog_pages}, manifest {manifest_pages}"
            )

    for key in manifest_records:
        if key not in catalog_records:
            errors.append(f"manifest item missing from catalog: {key[0]} / {key[1]}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Companion source-manifest validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validated 44 companion catalog entries against exact PDF source records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
