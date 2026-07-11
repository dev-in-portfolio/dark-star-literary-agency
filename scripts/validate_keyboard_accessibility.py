#!/usr/bin/env python3
"""Validate persistent keyboard, motion, link-recognition, and contrast safeguards."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLES = ROOT / "styles.css"

REQUIRED_CSS = {
    "global safeguard marker": "/* Global keyboard and contrast safeguards */",
    "native-control focus coverage": "input:focus-visible",
    "select focus coverage": "select:focus-visible",
    "textarea focus coverage": "textarea:focus-visible",
    "summary focus coverage": "summary:focus-visible",
    "inline-link recognition": "text-decoration: underline",
    "reduced-motion media query": "@media (prefers-reduced-motion: reduce)",
    "smooth-scroll override": "scroll-behavior: auto !important",
    "forced-colors media query": "@media (forced-colors: active)",
    "system focus color": "outline-color: Highlight",
}


def main() -> int:
    if not STYLES.is_file():
        print("Keyboard accessibility validation failed:\n- styles.css is missing")
        return 1

    css = STYLES.read_text(encoding="utf-8")
    errors = [label for label, token in REQUIRED_CSS.items() if token not in css]

    if errors:
        print("Keyboard accessibility validation failed:")
        for label in errors:
            print(f"- Missing {label}")
        return 1

    print(
        "Validated global keyboard focus, visible inline links, reduced motion, "
        "and forced-colors safeguards."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
