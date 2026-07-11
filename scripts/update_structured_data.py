#!/usr/bin/env python3
"""Generate conservative JSON-LD for the site identity and canonical storybooks."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "site-config.json"
MARKETPLACE_PATH = ROOT / "data" / "marketplace-records.json"
GENERATED_RE = re.compile(
    r"\s*<script\s+type=[\"']application/ld\+json[\"']\s+data-generated=[\"']structured-data[\"']>.*?</script>",
    re.IGNORECASE | re.DOTALL,
)
META_DESCRIPTION_RE = re.compile(
    r"<meta\b[^>]*\bname=[\"']description[\"'][^>]*\bcontent=[\"']([^\"']*)[\"'][^>]*>",
    re.IGNORECASE,
)
CANONICAL_RE = re.compile(
    r"<link\b[^>]*\brel=[\"']canonical[\"'][^>]*\bhref=[\"']([^\"']+)[\"'][^>]*>",
    re.IGNORECASE,
)
OG_IMAGE_RE = re.compile(
    r"<meta\b[^>]*\bproperty=[\"']og:image[\"'][^>]*\bcontent=[\"']([^\"']+)[\"'][^>]*>",
    re.IGNORECASE,
)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def require_string(data: dict, key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"Missing required configuration value: {key}")
    return value.strip()


def extract(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return html.unescape(match.group(1)).strip() if match else ""


def absolute(site_url: str, path: str) -> str:
    return urljoin(site_url.rstrip("/") + "/", path.lstrip("/"))


def json_script(payload: dict) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, indent=2).replace("</", "<\\/")
    indented = "\n".join("    " + line for line in encoded.splitlines())
    return (
        '    <script type="application/ld+json" data-generated="structured-data">\n'
        f"{indented}\n"
        "    </script>"
    )


def insert_generated(text: str, payload: dict) -> str:
    cleaned = GENERATED_RE.sub("", text)
    if "</head>" not in cleaned.lower():
        raise ValueError("missing </head>")
    return re.sub(
        r"\s*</head>",
        "\n" + json_script(payload) + "\n  </head>",
        cleaned,
        count=1,
        flags=re.IGNORECASE,
    )


def homepage_payload(config: dict[str, str]) -> dict:
    site_url = require_string(config, "site_url").rstrip("/")
    site_name = require_string(config, "site_name")
    author_name = require_string(config, "author_name")
    author_url = absolute(site_url, require_string(config, "author_path"))
    email = require_string(config, "contact_email")
    language = require_string(config, "language")

    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{site_url}/#organization",
                "name": site_name,
                "url": f"{site_url}/",
                "email": email,
                "founder": {"@id": f"{site_url}/#author"},
            },
            {
                "@type": "Person",
                "@id": f"{site_url}/#author",
                "name": author_name,
                "url": author_url,
            },
            {
                "@type": "WebSite",
                "@id": f"{site_url}/#website",
                "name": site_name,
                "url": f"{site_url}/",
                "inLanguage": language,
                "publisher": {"@id": f"{site_url}/#organization"},
            },
        ],
    }


def book_payload(config: dict[str, str], record: dict, text: str) -> dict:
    site_url = require_string(config, "site_url").rstrip("/")
    canonical = extract(CANONICAL_RE, text)
    description = extract(META_DESCRIPTION_RE, text)
    image = extract(OG_IMAGE_RE, text)
    if not canonical:
        raise ValueError("missing generated canonical URL")
    if not description:
        raise ValueError("missing meta description")

    title = record.get("title")
    number = record.get("book_number")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("marketplace record is missing title")
    if not isinstance(number, int) or number <= 0:
        raise ValueError("marketplace record has invalid book_number")

    payload: dict = {
        "@context": "https://schema.org",
        "@type": "Book",
        "@id": f"{canonical}#book",
        "name": title.strip(),
        "description": description,
        "url": canonical,
        "mainEntityOfPage": canonical,
        "inLanguage": require_string(config, "language"),
        "author": {"@id": f"{site_url}/#author", "@type": "Person", "name": require_string(config, "author_name")},
        "publisher": {"@id": f"{site_url}/#organization", "@type": "Organization", "name": require_string(config, "site_name")},
        "isPartOf": {
            "@type": "CreativeWorkSeries",
            "name": require_string(config, "series_name"),
            "url": absolute(site_url, require_string(config, "series_path")),
        },
        "additionalProperty": {
            "@type": "PropertyValue",
            "name": "Series position",
            "value": number,
        },
    }
    if image:
        payload["image"] = image
    return payload


def target_pages(config: dict, marketplace: dict) -> list[tuple[Path, dict]]:
    records = marketplace.get("records")
    if not isinstance(records, list) or len(records) != 10:
        raise SystemExit("marketplace registry must contain exactly ten canonical records")

    targets: list[tuple[Path, dict]] = [(ROOT / "index.html", homepage_payload(config))]
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise SystemExit("marketplace registry records must be objects")
        filename = record.get("filename")
        if not isinstance(filename, str) or not filename.strip():
            raise SystemExit("marketplace record is missing filename")
        if filename in seen:
            raise SystemExit(f"duplicate marketplace filename: {filename}")
        seen.add(filename)
        page = ROOT / "books" / filename
        if not page.is_file():
            raise SystemExit(f"missing canonical book page: {page.relative_to(ROOT)}")
        text = page.read_text(encoding="utf-8")
        targets.append((page, book_payload(config, record, text)))
    return targets


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Write generated JSON-LD into target pages")
    mode.add_argument("--check", action="store_true", help="Fail if generated JSON-LD is not current")
    args = parser.parse_args()

    config = load_json(CONFIG_PATH)
    marketplace = load_json(MARKETPLACE_PATH)
    changes: list[str] = []
    errors: list[str] = []

    for page, payload in target_pages(config, marketplace):
        relative = page.relative_to(ROOT).as_posix()
        try:
            original = page.read_text(encoding="utf-8")
            updated = insert_generated(original, payload)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")
            continue
        if updated != original:
            changes.append(relative)
            if args.write:
                page.write_text(updated, encoding="utf-8")

    if errors:
        print("Structured-data generation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    if args.check and changes:
        print("Structured data is not current. Run: python scripts/update_structured_data.py --write")
        for path in changes:
            print(f"- {path}")
        return 1

    action = "Updated" if args.write else "Validated"
    print(f"{action} structured data for the homepage and ten canonical storybooks.")
    if changes and args.write:
        print(f"Changed {len(changes)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
