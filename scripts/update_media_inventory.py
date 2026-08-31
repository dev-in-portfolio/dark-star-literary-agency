#!/usr/bin/env python3
"""Generate and validate a checksum-backed inventory of public media assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets"
INVENTORY_PATH = ROOT / "data" / "media-inventory.json"
BUDGET_PATH = ROOT / "data" / "media-budget.json"
ARCHIVE_PAGE = ROOT / "lulu-ellie" / "original-adventure" / "index.html"
ARCHIVE_SCRIPT = ROOT / "lulu-ellie" / "original-adventure" / "archive.js"
MEDIA_SCRIPT = ROOT / "media.js"
MEDIA_EXTENSIONS = {
    ".avif",
    ".gif",
    ".jpeg",
    ".jpg",
    ".mp4",
    ".png",
    ".svg",
    ".webm",
    ".webp",
}
VIDEO_EXTENSIONS = {".mp4", ".webm"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def media_files() -> list[Path]:
    if not ASSET_ROOT.is_dir():
        raise SystemExit("assets directory is missing")
    return sorted(
        path
        for path in ASSET_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS
    )


def build_inventory() -> dict:
    records: list[dict[str, object]] = []
    extension_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "bytes": 0})
    total_bytes = 0
    video_bytes = 0
    image_bytes = 0

    for path in media_files():
        relative = path.relative_to(ROOT).as_posix()
        extension = path.suffix.lower()
        size = path.stat().st_size
        total_bytes += size
        if extension in VIDEO_EXTENSIONS:
            video_bytes += size
            kind = "video"
        else:
            image_bytes += size
            kind = "image"
        extension_totals[extension]["files"] += 1
        extension_totals[extension]["bytes"] += size
        records.append(
            {
                "path": relative,
                "kind": kind,
                "extension": extension,
                "bytes": size,
                "sha256": sha256(path),
            }
        )

    largest = sorted(records, key=lambda record: int(record["bytes"]), reverse=True)[:20]
    return {
        "schema_version": 1,
        "asset_root": "assets",
        "summary": {
            "files": len(records),
            "total_bytes": total_bytes,
            "image_files": sum(1 for record in records if record["kind"] == "image"),
            "image_bytes": image_bytes,
            "video_files": sum(1 for record in records if record["kind"] == "video"),
            "video_bytes": video_bytes,
            "by_extension": dict(sorted(extension_totals.items())),
        },
        "largest_files": largest,
        "files": records,
    }


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def validate_budget(inventory: dict) -> list[str]:
    if not BUDGET_PATH.is_file():
        return ["data/media-budget.json is missing"]
    budget = load_json(BUDGET_PATH)
    summary = inventory["summary"]
    files = inventory["files"]
    errors: list[str] = []

    limits = {
        "max_total_bytes": int(summary["total_bytes"]),
        "max_video_bytes": int(summary["video_bytes"]),
        "max_image_bytes": int(summary["image_bytes"]),
    }
    for key, actual in limits.items():
        configured = budget.get(key)
        if not isinstance(configured, int) or configured <= 0:
            errors.append(f"media budget has invalid {key}")
        elif actual > configured:
            errors.append(f"{key} exceeded: {actual} > {configured}")

    per_file_limits = {
        "video": budget.get("max_video_file_bytes"),
        "image": budget.get("max_image_file_bytes"),
    }
    for kind, configured in per_file_limits.items():
        if not isinstance(configured, int) or configured <= 0:
            errors.append(f"media budget has invalid max_{kind}_file_bytes")
            continue
        for record in files:
            if record["kind"] == kind and int(record["bytes"]) > configured:
                errors.append(
                    f"{record['path']} exceeds max_{kind}_file_bytes: "
                    f"{record['bytes']} > {configured}"
                )

    return errors


def validate_delivery_policy() -> list[str]:
    errors: list[str] = []
    required_files = (ARCHIVE_PAGE, ARCHIVE_SCRIPT, MEDIA_SCRIPT)
    for path in required_files:
        if not path.is_file():
            errors.append(f"missing media-delivery file: {path.relative_to(ROOT)}")
    if errors:
        return errors

    archive_page = ARCHIVE_PAGE.read_text(encoding="utf-8")
    archive_script = ARCHIVE_SCRIPT.read_text(encoding="utf-8")
    media_script = MEDIA_SCRIPT.read_text(encoding="utf-8")

    page_requirements = (
        'href="archive.css"',
        'preload="none" poster="../../assets/lulu-ellie/original-adventure/book-20/front-cover.jpg"',
        "created and loaded only after a visitor selects a cover",
    )
    for requirement in page_requirements:
        if requirement not in archive_page:
            errors.append(f"archive page is missing deferred-media requirement: {requirement}")

    archive_requirements = (
        'make("button", "media-load-button")',
        'button.addEventListener("click"',
        'image.loading = "lazy"',
        'image.decoding = "async"',
        'image.fetchPriority = "low"',
        'video.preload = "metadata"',
    )
    for requirement in archive_requirements:
        if requirement not in archive_script:
            errors.append(f"archive.js is missing click-to-load requirement: {requirement}")

    if 'video.preload = "none"' not in media_script:
        errors.append("media.js must keep automatic videos at preload=none")
    if 'video.preload = "metadata"' in media_script:
        errors.append("media.js must not upgrade automatic videos to metadata preload")

    return errors


def serialized(inventory: dict) -> str:
    return json.dumps(inventory, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Write the current media inventory")
    mode.add_argument("--check", action="store_true", help="Fail if inventory, budgets, or delivery policy are stale")
    args = parser.parse_args()

    inventory = build_inventory()
    generated = serialized(inventory)
    current = INVENTORY_PATH.read_text(encoding="utf-8") if INVENTORY_PATH.is_file() else ""
    errors = validate_budget(inventory) + validate_delivery_policy()

    if args.write:
        INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        INVENTORY_PATH.write_text(generated, encoding="utf-8")
        print(
            "Updated media inventory: "
            f"{inventory['summary']['files']} files, "
            f"{inventory['summary']['total_bytes']} bytes total."
        )
        if errors:
            print("Media budget or delivery-policy validation failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        return 0

    if generated != current:
        errors.insert(0, "media inventory is stale; run: python scripts/update_media_inventory.py --write")

    if errors:
        print("Media inventory validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Validated media inventory, budgets, and deferred-delivery policy: "
        f"{inventory['summary']['files']} files, "
        f"{inventory['summary']['total_bytes']} bytes total."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
