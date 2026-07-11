#!/usr/bin/env python3
"""Validate PDF accessibility audit records and prevent premature public PDF release claims."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "companion-source-manifest.csv"
AUDIT_PATH = ROOT / "data" / "pdf-accessibility-audit.json"
HTML_LINK_RE = re.compile(r"href=[\"']([^\"']+\.pdf(?:[?#][^\"']*)?)[\"']", re.IGNORECASE)

ALLOWED_REMEDIATION = {
    "not-started",
    "ocr-draft",
    "semantic-tagging",
    "manual-qa",
    "approved",
}
ALLOWED_RELEASE = {
    "blocked-for-accessible-digital-distribution",
    "accessible-digital-release-approved",
}


def load_manifest() -> dict[str, dict[str, str]]:
    try:
        with MANIFEST_PATH.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        raise SystemExit(f"Could not read source manifest: {exc}") from exc

    if len(rows) != 44:
        raise SystemExit(f"Expected 44 source records, found {len(rows)}")

    records: dict[str, dict[str, str]] = {}
    for row in rows:
        record_id = (row.get("id") or "").strip()
        if not record_id or record_id in records:
            raise SystemExit(f"Invalid or duplicate source ID: {record_id!r}")
        records[record_id] = row
    return records


def load_audit() -> dict:
    try:
        value = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read accessibility audit: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("Accessibility audit must contain a JSON object")
    return value


def validate_public_pdf_links(approved_ids: set[str]) -> list[str]:
    errors: list[str] = []
    for page in sorted(ROOT.rglob("*.html")):
        if any(part.startswith(".") for part in page.relative_to(ROOT).parts):
            continue
        text = page.read_text(encoding="utf-8")
        for match in HTML_LINK_RE.finditer(text):
            href = match.group(1)
            if href.startswith(("http://", "https://")):
                errors.append(
                    f"{page.relative_to(ROOT)} links directly to external PDF {href}; "
                    "record an approved accessible edition before publishing a PDF link"
                )
                continue
            matching = [record_id for record_id in approved_ids if record_id in href]
            if not matching:
                errors.append(
                    f"{page.relative_to(ROOT)} links to PDF {href} without an approved accessibility record"
                )
    return errors


def main() -> int:
    manifest = load_manifest()
    audit = load_audit()
    errors: list[str] = []

    if audit.get("schema_version") != 1:
        errors.append("pdf accessibility audit must use schema_version 1")
    if audit.get("audit_date") != "2026-07-11":
        errors.append("pdf accessibility audit must preserve the documented 2026-07-11 baseline audit date")
    if audit.get("baseline_result") != "no-usable-extractable-text-detected":
        errors.append("baseline_result must state that no usable extractable text was detected")

    records = audit.get("records")
    if not isinstance(records, list) or len(records) != 44:
        errors.append("pdf accessibility audit must contain exactly 44 records")
        records = []

    seen: set[str] = set()
    approved_ids: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            errors.append("accessibility records must be JSON objects")
            continue
        record_id = record.get("id")
        if not isinstance(record_id, str) or record_id not in manifest:
            errors.append(f"unknown accessibility record ID: {record_id!r}")
            continue
        if record_id in seen:
            errors.append(f"duplicate accessibility record ID: {record_id}")
            continue
        seen.add(record_id)
        source = manifest[record_id]

        if record.get("source_sha256") != source["sha256"]:
            errors.append(f"{record_id}: source SHA-256 does not match companion manifest")
        if record.get("source_file") != source["source_file"]:
            errors.append(f"{record_id}: source filename does not match companion manifest")
        if record.get("pages") != int(source["pages"]):
            errors.append(f"{record_id}: page count does not match companion manifest")

        remediation = record.get("remediation_status")
        release = record.get("release_status")
        if remediation not in ALLOWED_REMEDIATION:
            errors.append(f"{record_id}: invalid remediation_status {remediation!r}")
        if release not in ALLOWED_RELEASE:
            errors.append(f"{record_id}: invalid release_status {release!r}")

        if release == "accessible-digital-release-approved":
            approved_ids.add(record_id)
            required = {
                "text_layer": "present-and-manually-verified",
                "tagged_pdf": "verified",
                "reading_order": "verified",
                "meaningful_alt_text": "verified",
                "language_metadata": "verified",
                "remediation_status": "approved",
            }
            for key, expected in required.items():
                if record.get(key) != expected:
                    errors.append(
                        f"{record_id}: accessible release requires {key}={expected!r}, "
                        f"found {record.get(key)!r}"
                    )
        else:
            if record.get("text_layer") == "present-and-manually-verified" and remediation == "approved":
                errors.append(f"{record_id}: approved remediation must use accessible release status")

    missing = sorted(set(manifest) - seen)
    extra = sorted(seen - set(manifest))
    if missing:
        errors.append(f"missing accessibility records: {', '.join(missing)}")
    if extra:
        errors.append(f"unexpected accessibility records: {', '.join(extra)}")

    errors.extend(validate_public_pdf_links(approved_ids))

    if errors:
        print("PDF accessibility validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    blocked = sum(
        1 for record in records if record.get("release_status") == "blocked-for-accessible-digital-distribution"
    )
    print(
        "Validated PDF accessibility registry: "
        f"{len(records)} source interiors, {blocked} blocked pending remediation, "
        f"{len(approved_ids)} approved accessible digital editions."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
