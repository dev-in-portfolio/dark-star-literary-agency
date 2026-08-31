#!/usr/bin/env python3
"""Normalize canonical/social metadata and generate sitemap.xml for the static site."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "site-config.json"
SITEMAP_PATH = ROOT / "sitemap.xml"
ROBOTS_PATH = ROOT / "robots.txt"
IGNORED_PARTS = {".git", ".github", ".netlify", "node_modules"}

CANONICAL_RE = re.compile(r"\s*<link\b[^>]*\brel=[\"']canonical[\"'][^>]*>", re.IGNORECASE)
META_RE_TEMPLATE = r"\s*<meta\b[^>]*(?:property|name)=[\"']{key}[\"'][^>]*>"
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
DESCRIPTION_RE = re.compile(
    r"<meta\b[^>]*\bname=[\"']description[\"'][^>]*\bcontent=[\"']([^\"']*)[\"'][^>]*>",
    re.IGNORECASE,
)
OG_TITLE_RE = re.compile(
    r"<meta\b[^>]*\bproperty=[\"']og:title[\"'][^>]*\bcontent=[\"']([^\"']*)[\"'][^>]*>",
    re.IGNORECASE,
)
OG_DESCRIPTION_RE = re.compile(
    r"<meta\b[^>]*\bproperty=[\"']og:description[\"'][^>]*\bcontent=[\"']([^\"']*)[\"'][^>]*>",
    re.IGNORECASE,
)
REFRESH_RE = re.compile(
    r"<meta\b[^>]*\bhttp-equiv=[\"']refresh[\"'][^>]*\bcontent=[\"'][^\"']*url\s*=\s*([^\"';]+)[^\"']*[\"'][^>]*>",
    re.IGNORECASE,
)
IMG_RE = re.compile(r"<img\b([^>]*)>", re.IGNORECASE | re.DOTALL)
SRC_RE = re.compile(r"\bsrc=[\"']([^\"']+)[\"']", re.IGNORECASE)
ALT_RE = re.compile(r"\balt=[\"']([^\"']*)[\"']", re.IGNORECASE)
ROBOTS_META_RE = re.compile(
    r"<meta\\b[^>]*\\bname=[\"\']robots[\"\'][^>]*\\bcontent=[\"\']([^\"\']*)[\"\'][^>]*>",
    re.IGNORECASE,
)

MANAGED_META_KEYS = (
    "og:url",
    "og:site_name",
    "og:locale",
    "og:image",
    "og:image:alt",
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
    "twitter:image:alt",
)


def load_config() -> dict[str, str]:
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read {CONFIG_PATH.relative_to(ROOT)}: {exc}") from exc

    required = ("site_name", "site_url", "language", "twitter_card_without_image", "twitter_card_with_image")
    missing = [key for key in required if not isinstance(config.get(key), str) or not config[key].strip()]
    if missing:
        raise SystemExit(f"Missing site configuration values: {', '.join(missing)}")

    config["site_url"] = config["site_url"].rstrip("/")
    parsed = urlsplit(config["site_url"])
    if parsed.scheme != "https" or not parsed.netloc:
        raise SystemExit("site_url must be an absolute HTTPS URL")
    return config


def html_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.html")
        if not any(part in IGNORED_PARTS for part in path.parts)
    )


def public_path(page: Path) -> str:
    relative = page.relative_to(ROOT).as_posix()
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        return "/" + relative[: -len("index.html")]
    return "/" + quote(relative)


def absolute_page_url(page: Path, site_url: str) -> str:
    return site_url + public_path(page)


def find_content(pattern: re.Pattern[str], text: str, fallback: str = "") -> str:
    match = pattern.search(text)
    return " ".join(html.unescape(match.group(1)).split()) if match else fallback


def escape_attr(value: str) -> str:
    return html.escape(value, quote=True)


def remove_managed_metadata(text: str) -> str:
    text = CANONICAL_RE.sub("", text)
    for key in MANAGED_META_KEYS:
        pattern = re.compile(META_RE_TEMPLATE.format(key=re.escape(key)), re.IGNORECASE)
        text = pattern.sub("", text)
    return text


def first_local_image(page: Path, page_url: str, text: str) -> tuple[str, str] | None:
    for image_match in IMG_RE.finditer(text):
        attrs = image_match.group(1)
        source_match = SRC_RE.search(attrs)
        if not source_match:
            continue
        source = source_match.group(1).strip()
        parsed = urlsplit(source)
        if parsed.scheme in {"http", "https"}:
            absolute = source
        elif parsed.scheme or source.startswith("data:"):
            continue
        else:
            absolute = urljoin(page_url, source)

        alt_match = ALT_RE.search(attrs)
        alt = " ".join(html.unescape(alt_match.group(1)).split()) if alt_match else ""
        return absolute, alt
    return None


def redirect_target(page_url: str, text: str) -> str | None:
    match = REFRESH_RE.search(text)
    if not match:
        return None
    return urljoin(page_url, match.group(1).strip())


def build_metadata(page: Path, text: str, config: dict[str, str]) -> tuple[str, bool, bool]:
    page_url = absolute_page_url(page, config["site_url"])
    redirect_url = redirect_target(page_url, text)
    canonical_url = redirect_url or page_url

    title = find_content(OG_TITLE_RE, text) or find_content(TITLE_RE, text, config["site_name"])
    description = find_content(OG_DESCRIPTION_RE, text) or find_content(DESCRIPTION_RE, text)
    image = first_local_image(page, page_url, text)
    if image is None:
        image = (config["site_url"].rstrip("/") + "/web-image/og-image.png", config["site_name"])
    robots = find_content(ROBOTS_META_RE, text).lower()
    is_noindex = "noindex" in {part.strip() for part in robots.split(",")} if robots else False

    lines = [
        f'    <link rel="canonical" href="{escape_attr(canonical_url)}">',
        f'    <meta property="og:url" content="{escape_attr(canonical_url)}">',
        f'    <meta property="og:site_name" content="{escape_attr(config["site_name"])}">',
        f'    <meta property="og:locale" content="{escape_attr(config["language"].replace("-", "_"))}">',
    ]

    if image:
        image_url, image_alt = image
        lines.append(f'    <meta property="og:image" content="{escape_attr(image_url)}">')
        if image_alt:
            lines.append(f'    <meta property="og:image:alt" content="{escape_attr(image_alt)}">')
        lines.append(f'    <meta name="twitter:card" content="{escape_attr(config["twitter_card_with_image"])}">')
    else:
        lines.append(f'    <meta name="twitter:card" content="{escape_attr(config["twitter_card_without_image"])}">')

    lines.append(f'    <meta name="twitter:title" content="{escape_attr(title)}">')
    if description:
        lines.append(f'    <meta name="twitter:description" content="{escape_attr(description)}">')
    if image:
        image_url, image_alt = image
        lines.append(f'    <meta name="twitter:image" content="{escape_attr(image_url)}">')
        if image_alt:
            lines.append(f'    <meta name="twitter:image:alt" content="{escape_attr(image_alt)}">')

    cleaned = remove_managed_metadata(text)
    if "</head>" not in cleaned.lower():
        raise ValueError("missing </head>")
    updated = re.sub(r"\s*</head>", "\n" + "\n".join(lines) + "\n  </head>", cleaned, count=1, flags=re.IGNORECASE)
    return updated, redirect_url is not None, is_noindex


def sitemap_xml(urls: list[str]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in sorted(urls):
        lines.extend(("  <url>", f"    <loc>{html.escape(url)}</loc>", "  </url>"))
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def robots_text(site_url: str) -> str:
    existing = ROBOTS_PATH.read_text(encoding="utf-8") if ROBOTS_PATH.is_file() else "User-agent: *\nAllow: /\n"
    kept = [line.rstrip() for line in existing.splitlines() if not line.lower().startswith("sitemap:")]
    while kept and not kept[-1]:
        kept.pop()
    kept.extend(("", f"Sitemap: {site_url}/sitemap.xml"))
    return "\n".join(kept) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Update HTML, robots.txt, and sitemap.xml in place")
    mode.add_argument("--check", action="store_true", help="Fail if generated SEO files are not current")
    args = parser.parse_args()

    config = load_config()
    changed: list[str] = []
    errors: list[str] = []
    sitemap_urls: list[str] = []

    for page in html_files():
        relative = page.relative_to(ROOT).as_posix()
        try:
            original = page.read_text(encoding="utf-8")
            updated, is_redirect, is_noindex = build_metadata(page, original, config)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")
            continue

        if not is_redirect and not is_noindex:
            sitemap_urls.append(absolute_page_url(page, config["site_url"]))

        if updated != original:
            changed.append(relative)
            if args.write:
                page.write_text(updated, encoding="utf-8")

    generated_sitemap = sitemap_xml(sitemap_urls)
    current_sitemap = SITEMAP_PATH.read_text(encoding="utf-8") if SITEMAP_PATH.is_file() else ""
    if generated_sitemap != current_sitemap:
        changed.append("sitemap.xml")
        if args.write:
            SITEMAP_PATH.write_text(generated_sitemap, encoding="utf-8")

    generated_robots = robots_text(config["site_url"])
    current_robots = ROBOTS_PATH.read_text(encoding="utf-8") if ROBOTS_PATH.is_file() else ""
    if generated_robots != current_robots:
        changed.append("robots.txt")
        if args.write:
            ROBOTS_PATH.write_text(generated_robots, encoding="utf-8")

    if errors:
        print("SEO generation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    if args.check and changed:
        print("SEO files are not current. Run: python scripts/update_seo.py --write")
        for path in changed:
            print(f"- {path}")
        return 1

    action = "Updated" if args.write else "Validated"
    print(f"{action} canonical/social metadata for {len(html_files())} HTML pages and {len(sitemap_urls)} sitemap URLs.")
    if changed and args.write:
        print(f"Changed {len(changed)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
