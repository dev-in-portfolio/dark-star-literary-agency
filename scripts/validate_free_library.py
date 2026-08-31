#!/usr/bin/env python3
"""Validate the public Free Library manifest, viewer surfaces, and navigation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "free-library.json"
IGNORED_PARTS = {".git", ".github", ".netlify", "node_modules"}

EXPECTED_REPOS = {
    "l_e_storage",
    "l_e_storage2",
    "l_e_storage3",
    "l_e_storage4",
    "l_e_storage5",
    "l_e_storage6",
    "l_e_storage7",
}

KIND_BY_EXTENSION = {
    "pdf": "document",
    "mp3": "audio",
    "mp4": "video",
    "png": "image",
    "jpg": "image",
    "jpeg": "image",
    "webp": "image",
}


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def is_redirect(text: str) -> bool:
    lowered = text.lower()
    return 'http-equiv="refresh"' in lowered or "http-equiv='refresh'" in lowered


def main() -> int:
    errors: list[str] = []

    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Could not read data/free-library.json: {exc}")
        return 1

    if manifest.get("schema_version") != 1:
        fail("free-library schema_version must be 1", errors)

    if manifest.get("policy", {}).get("public_free_access") is not True:
        fail("free-library manifest must explicitly enable public_free_access", errors)

    sources = manifest.get("source_repositories")
    assets = manifest.get("assets")

    if not isinstance(sources, list) or len(sources) != 7:
        fail("free-library manifest must define exactly seven source repositories", errors)
        sources = []
    if not isinstance(assets, list):
        fail("free-library assets must be a list", errors)
        assets = []

    source_by_repo = {
        item.get("repo"): item
        for item in sources
        if isinstance(item, dict) and isinstance(item.get("repo"), str)
    }

    if set(source_by_repo) != EXPECTED_REPOS:
        fail("free-library source repositories must be l_e_storage through l_e_storage7", errors)

    if manifest.get("asset_count") != len(assets):
        fail("free-library asset_count does not equal the number of asset records", errors)

    if sum(int(item.get("asset_count", 0)) for item in sources if isinstance(item, dict)) != len(assets):
        fail("free-library per-repository counts do not sum to the manifest asset total", errors)

    keys: set[str] = set()
    counted_by_repo = {repo: 0 for repo in EXPECTED_REPOS}

    for index, asset in enumerate(assets, start=1):
        if not isinstance(asset, dict):
            fail(f"asset #{index} is not an object", errors)
            continue

        key = asset.get("key")
        repo = asset.get("repo")
        ref = asset.get("ref")
        path = asset.get("path")
        filename = asset.get("filename")
        extension = str(asset.get("extension", "")).lower()
        kind = asset.get("kind")
        source_url = asset.get("source_url")
        download_url = asset.get("download_url")

        if not isinstance(key, str) or not key:
            fail(f"asset #{index} is missing a key", errors)
        elif key in keys:
            fail(f"duplicate free-library key: {key}", errors)
        else:
            keys.add(key)

        if repo not in EXPECTED_REPOS:
            fail(f"{key or index}: invalid repository {repo!r}", errors)
            continue
        counted_by_repo[repo] += 1

        source = source_by_repo.get(repo, {})
        if ref != source.get("commit"):
            fail(f"{key}: asset ref does not match its pinned source commit", errors)

        if not isinstance(path, str) or not path:
            fail(f"{key}: missing source path", errors)
            continue

        if filename != Path(path).name:
            fail(f"{key}: filename does not match the source path", errors)

        expected_kind = KIND_BY_EXTENSION.get(extension)
        if expected_kind is None:
            fail(f"{key}: unsupported public extension {extension!r}", errors)
        elif kind != expected_kind:
            fail(f"{key}: kind {kind!r} does not match extension {extension!r}", errors)

        if any(part in {".github", ".transfer"} for part in Path(path).parts):
            fail(f"{key}: internal repository plumbing leaked into the public archive", errors)

        expected_blob_prefix = f"https://github.com/dev-in-portfolio/{repo}/blob/{ref}/"
        expected_raw_prefix = f"https://github.com/dev-in-portfolio/{repo}/raw/{ref}/"
        if not isinstance(source_url, str) or not source_url.startswith(expected_blob_prefix):
            fail(f"{key}: source_url is not pinned to the authoritative repository commit", errors)
        if not isinstance(download_url, str) or not download_url.startswith(expected_raw_prefix):
            fail(f"{key}: download_url is not pinned to the authoritative repository commit", errors)

    for repo, count in counted_by_repo.items():
        expected = int(source_by_repo.get(repo, {}).get("asset_count", -1))
        if count != expected:
            fail(f"{repo}: manifest contains {count} assets but source record says {expected}", errors)

    required_files = (
        ROOT / "free-library.html",
        ROOT / "free-viewer.html",
        ROOT / "free-library.js",
        ROOT / "free-viewer.js",
    )
    for path in required_files:
        if not path.is_file():
            fail(f"missing Free Library surface: {path.relative_to(ROOT)}", errors)

    viewer = ROOT / "free-viewer.html"
    if viewer.is_file():
        text = viewer.read_text(encoding="utf-8")
        if 'name="robots" content="noindex,follow"' not in text:
            fail("free-viewer.html must stay noindex,follow", errors)
        if "free-viewer.js" not in text:
            fail("free-viewer.html is missing free-viewer.js", errors)

    library_page = ROOT / "free-library.html"
    if library_page.is_file():
        text = library_page.read_text(encoding="utf-8")
        for phrase in ("Free Library", "Download free", "free-library.js"):
            if phrase not in text:
                fail(f"free-library.html missing required public access language: {phrase}", errors)

    for page in ROOT.rglob("*.html"):
        if any(part in IGNORED_PARTS for part in page.parts):
            continue
        text = page.read_text(encoding="utf-8")
        if is_redirect(text):
            continue
        if '<nav class="nav" aria-label="Primary">' in text and "free-library.html" not in text:
            fail(f"{page.relative_to(ROOT)}: primary navigation is missing Free Library", errors)

    if errors:
        print("Free Library validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Validated {len(assets)} free public storage assets across seven repositories, "
        "plus viewer/download surfaces and global Free Library navigation."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
