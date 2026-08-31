#!/usr/bin/env python3
"""Single release entrypoint shared by GitHub Actions and Netlify."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GENERATORS = [
    ["python3", "scripts/reconcile_catalog.py", "--write"],
    ["python3", "scripts/update_seo.py", "--write"],
    ["python3", "scripts/update_structured_data.py", "--write"],
    ["python3", "scripts/update_media_inventory.py", "--write"],
]

VALIDATORS = [
    ["python3", "scripts/validate_library_master.py"],
    ["python3", "scripts/validate_site.py"],
    ["python3", "scripts/validate_source_manifest.py"],
    ["python3", "scripts/validate_marketplace.py"],
    ["python3", "scripts/update_seo.py", "--check"],
    ["python3", "scripts/update_structured_data.py", "--check"],
    ["python3", "scripts/update_media_inventory.py", "--check"],
    ["python3", "scripts/validate_pdf_accessibility.py"],
    ["python3", "scripts/validate_interaction_semantics.py"],
]


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    try:
        for command in GENERATORS:
            run(command)
        for command in VALIDATORS:
            run(command)
    except subprocess.CalledProcessError as exc:
        return int(exc.returncode or 1)
    print("Release preparation and all validations passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
