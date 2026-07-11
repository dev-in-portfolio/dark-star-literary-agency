#!/usr/bin/env python3
"""Run the complete static-site release validation suite with one interpreter."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("site integrity", ("scripts/validate_site.py",)),
    ("source manifest", ("scripts/validate_source_manifest.py",)),
    ("marketplace claims", ("scripts/validate_marketplace.py",)),
    ("SEO and sitemap", ("scripts/update_seo.py", "--check")),
    ("structured data", ("scripts/update_structured_data.py", "--check")),
    ("media inventory", ("scripts/update_media_inventory.py", "--check")),
    ("PDF accessibility", ("scripts/validate_pdf_accessibility.py",)),
    ("interaction semantics", ("scripts/validate_interaction_semantics.py",)),
)


def main() -> int:
    for label, arguments in CHECKS:
        command = (sys.executable, *arguments)
        print(f"\n=== {label} ===", flush=True)
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode != 0:
            print(
                f"Release validation stopped at {label!r} "
                f"with exit code {completed.returncode}.",
                file=sys.stderr,
            )
            return completed.returncode

    print("\nAll eight release checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
