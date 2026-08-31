#!/usr/bin/env python3
"""Reconcile the public static site with the canonical Lulu & Ellie library catalog."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "library-master.json"
MARKETPLACE = ROOT / "data" / "marketplace-records.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def root_prefix(page: Path) -> str:
    depth = len(page.relative_to(ROOT).parts) - 1
    return "../" * depth


def header(prefix: str, current: str = "library") -> str:
    items = [
        ("home", "Home", f"{prefix}index.html"),
        ("dark-star", "Dark Star", f"{prefix}agency.html"),
        ("author", "About the Author", f"{prefix}ambrose-caspian-vale.html"),
        ("lulu", "Lulu &amp; Ellie", f"{prefix}lulu-ellie/"),
        ("library", "Library", f"{prefix}library.html"),
        ("parents", "Parents &amp; Teachers", f"{prefix}parents-teachers.html"),
        ("contact", "Contact", f"{prefix}contact.html"),
    ]
    links = "".join(
        f'<a href="{href}"' + (' aria-current="page"' if key == current else "") + f'>{label}</a>'
        for key, label, href in items
    )
    return f"""<a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header">
      <div class="header-inner">
        <a class="brand" href="{prefix}index.html" aria-label="Dark Star Literary Agency home">
          <span class="brand-orb" aria-hidden="true"></span>
          <span>Dark Star Literary Agency</span>
        </a>
        <nav class="nav" aria-label="Primary">{links}</nav>
      </div>
    </header>"""


def footer(prefix: str) -> str:
    return f"""<footer class="site-footer">
      <div class="site-shell footer-inner">
        <strong>&copy; 2026 Dark Star Literary Agency. All rights reserved.</strong>
        <div>Dark Star Literary Agency is the creative home of Ambrose Caspian Vale and the Lulu &amp; Ellie Adventures.</div>
        <div><a href="{prefix}accessibility.html">Accessibility</a> · Contact: <a href="mailto:literary@darkstarconsultinggroup.com">literary@darkstarconsultinggroup.com</a></div>
      </div>
    </footer>"""


def head(title: str, description: str, prefix: str, extra: str = "") -> str:
    return f"""  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(description)}">
    <meta property="og:type" content="website">
    <link rel="stylesheet" href="{prefix}styles.css">
    <link rel="stylesheet" href="{prefix}accessibility.css">
    <link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
{extra}  </head>"""


def original_series(master: dict) -> dict:
    return next(series for series in master["series"] if series["id"] == "original-adventure")


def marketplace_map() -> dict[int, dict]:
    data = load_json(MARKETPLACE)
    return {int(record["book_number"]): record for record in data.get("records", [])}


def original_book_page(book: dict, books: list[dict]) -> str:
    number = int(book["number"])
    title = book["title"]
    slug = book["slug"]
    prefix = "../"
    cover_ext = "png" if number == 1 else "jpg"
    cover = f"../assets/lulu-ellie/original-adventure/book-{number}/front-cover.{cover_ext}"
    feature = f"../assets/lulu-ellie/original-adventure/book-{number}/feature-page.png"
    video = f"../assets/lulu-ellie/original-adventure/book-{number}/animated-cover.mp4"
    prev_book = books[number - 2] if number > 1 else None
    next_book = books[number] if number < len(books) else None
    nav = []
    if prev_book:
        nav.append(f'<a class="button secondary" href="../books/{prev_book["slug"]}.html">Previous: Book {prev_book["number"]}</a>')
    nav.append('<a class="button" href="../series/lulu-and-ellie-adventures.html">Back to Series</a>')
    if next_book:
        nav.append(f'<a class="button secondary" href="../books/{next_book["slug"]}.html">Next: Book {next_book["number"]}</a>')
    description = f"{title} is Book {number} in the Lulu & Ellie Original Adventure series. The full source book is archived; current marketplace status is unverified."
    return f"""<!doctype html>
<html lang="en" data-nav="library">
{head(title + " | Lulu & Ellie Adventures", description, prefix)}
  <body data-nav="library">
    {header(prefix, "library")}
    <main id="main">
      <section class="page-hero">
        <div class="site-shell">
          <div class="breadcrumbs"><a href="../library.html">Library</a><span>→</span><a href="../series/lulu-and-ellie-adventures.html">Lulu &amp; Ellie Adventures</a><span>→</span><span>{esc(title)}</span></div>
          <div class="book-layout">
            <aside class="book-cover">
              <div class="book-cover-art has-image"><img src="{cover}" alt="{esc(title)} cover art"></div>
              <div class="book-meta">
                <span class="page-badge">Full source book archived</span>
                <div class="book-meta-grid">
                  <div><strong>Series</strong><span>Lulu &amp; Ellie Adventures</span></div>
                  <div><strong>Book</strong><span>Book {number}</span></div>
                  <div><strong>Marketplace</strong><span>Current status unverified</span></div>
                  <div><strong>Public claim</strong><span>No price or orderability asserted</span></div>
                </div>
              </div>
            </aside>
            <article class="hero-panel">
              <div class="eyebrow">Lulu &amp; Ellie Adventures · Book {number}</div>
              <h1>{esc(title)}</h1>
              <p class="lede">A source-confirmed full book in the Original Adventure sequence.</p>
              <p class="support-note">This page confirms the book and its place in the series. Marketplace availability is kept separate and remains unverified until an official listing is reviewed.</p>
            </article>
          </div>
        </div>
      </section>
      <section>
        <div class="site-shell section-card">
          <div class="section-head"><div class="section-kicker">Story Gallery</div><h2>Cover, motion, and interior feature art.</h2></div>
          <div class="book-media-grid">
            <article class="card book-media-card"><img src="{cover}" alt="{esc(title)} cover art" loading="lazy" decoding="async"><div class="card-copy"><h3>Cover Art</h3><p>The source-matched cover for Book {number}.</p></div></article>
            <article class="card book-media-card"><video muted loop playsinline preload="metadata" poster="{cover}"><source src="{video}" type="video/mp4">Your browser does not support the animated cover preview.</video><div class="card-copy"><h3>Motion Preview</h3><p>An optional animated preview from the matching archive folder.</p></div></article>
            <article class="card book-media-card"><img src="{feature}" alt="{esc(title)} interior feature art" loading="lazy" decoding="async"><div class="card-copy"><h3>Interior Feature Art</h3><p>A story-world feature image from the matching archive folder.</p></div></article>
          </div>
        </div>
      </section>
      <section id="marketplace">
        <div class="site-shell section-card">
          <div class="section-head"><div class="section-kicker">Marketplace Status</div><h2>Current marketplace status is unverified.</h2><p class="section-lede">No purchase button is shown until a current official product destination is verified.</p></div>
          <div class="section-actions"><a class="button secondary" href="../contact.html">Ask about availability</a></div>
        </div>
      </section>
      <section><div class="site-shell section-card"><div class="section-head"><div class="section-kicker">Explore More</div><h2>Continue the Original Adventure sequence.</h2></div><div class="book-nav">{''.join(nav)}</div></div></section>
    </main>
    {footer(prefix)}
  </body>
</html>
"""


def render_original_series(master: dict, market: dict[int, dict]) -> str:
    series = original_series(master)
    books = series["books"]
    cards = []
    purchases = []
    for book in books:
        n = int(book["number"])
        record = market.get(n)
        if record and record.get("url"):
            status = "Amazon link on file"
        elif record and not record.get("url"):
            status = "No active marketplace link"
        else:
            status = "Marketplace status unverified"
        cards.append(f"""<article class="book-list-card">
          <div class="tag-row"><span class="book-number">Book {n}</span><span class="status-badge">{esc(status)}</span></div>
          <h3>{esc(book["title"])}</h3>
          <p>Canonical Original Adventure Book {n}. The full source book and matching media are archived.</p>
          <div class="section-actions"><a class="button ghost" href="../books/{book["slug"]}.html">Explore Book</a></div>
        </article>""")
        if record and record.get("url"):
            purchases.append(f'<article class="card purchase-card"><div class="purchase-meta"><strong>Book {n} — {esc(book["title"])}</strong><span>Amazon link on file · current status unverified</span></div><a class="button" href="{esc(record["url"])}">Check Amazon</a></article>')
    description = "Explore all 20 source-confirmed Lulu & Ellie Original Adventure books in canonical story order, with marketplace claims kept separate from source-book verification."
    return f"""<!doctype html>
<html lang="en" data-nav="library">
{head("Lulu & Ellie Adventures | Original Adventure Storybook Series", description, "../")}
  <body data-nav="library">
    {header("../", "library")}
    <main id="main">
      <section class="page-hero"><div class="site-shell hero-grid"><article class="hero-panel"><div class="eyebrow">Original Adventure Storybook Series</div><h1>Lulu &amp; Ellie Adventures</h1><p class="lede">Twenty source-confirmed books in one canonical story sequence.</p><p class="lede">Book existence, marketplace availability, price, and orderability are tracked separately so the catalog can stay accurate without pretending an archive file is a live storefront.</p><div class="hero-actions"><a class="button" href="#books">Explore Books 1–20</a><a class="button secondary" href="#marketplace-links">Recorded marketplace links</a><a class="button secondary" href="../lulu-ellie/original-adventure/">Open the media archive</a></div></article><aside class="tier-hero-media"><img src="../assets/lulu-ellie/original-adventure/book-20/front-cover.jpg" alt="Lulu &amp; Ellie and the Keeper Ring cover art" loading="eager" decoding="async"></aside></div></section>
      <section><div class="site-shell section-card"><div class="section-head"><div class="section-kicker">Canonical Story Order</div><h2>Original Adventure Books 1–20</h2><p class="section-lede">The sequence below is sourced from the full books and their numbered archive mapping.</p></div><div id="books" class="book-list-grid">{''.join(cards)}</div></div></section>
      <section id="marketplace-links"><div class="site-shell section-card"><div class="section-head"><div class="section-kicker">Recorded Marketplace Links</div><h2>Marketplace evidence stays separate from the book catalog.</h2><p class="section-lede">Only recorded official destinations are linked. Current price, format, stock, and orderability must be confirmed at the destination.</p></div><div class="purchase-list">{''.join(purchases) if purchases else '<article class="card"><p>No verified marketplace links are currently published.</p></article>'}</div></div></section>
      <section><div class="site-shell section-card"><div class="section-actions"><a class="button" href="../lulu-ellie/">Lulu &amp; Ellie Hub</a><a class="button secondary" href="../library.html">Full Library</a><a class="button secondary" href="../contact.html">Contact Dark Star</a></div></div></section>
    </main>
    {footer("../")}
  </body>
</html>
"""


def render_archive(master: dict) -> tuple[str, str]:
    books = original_series(master)["books"]
    lis = "".join(f"<li>Book {book['number']} — {esc(book['title'])}</li>" for book in books)
    page = f"""<!doctype html>
<html lang="en" data-nav="library">
{head("Original Adventure Media Archive | Lulu & Ellie Adventures", "Explore the complete 20-book Original Adventure media archive with source-confirmed titles, cover art, motion previews, and interior feature pages.", "../../", '    <link rel="stylesheet" href="archive.css">\n    <script src="archive.js" defer></script>\n    <script src="../../media.js" defer></script>\n')}
  <body data-nav="library">
    {header("../../", "lulu")}
    <main id="main">
      <section class="page-hero"><div class="site-shell hero-grid"><article class="hero-panel"><div class="eyebrow">Original Adventure</div><h1>A complete 20-book media archive.</h1><p class="lede">All twenty full books now have source-confirmed titles and canonical book pages. Marketplace status remains a separate question and is never inferred from archive existence.</p><div class="hero-actions"><a class="button" href="#named-books">Books 1–20</a><a class="button secondary" href="#feature-pages">Interior media</a><a class="button secondary" href="../../series/lulu-and-ellie-adventures.html">Series page</a></div></article><aside class="panel tier-hero-media" aria-label="Animated Original Adventure archive preview"><video muted loop playsinline preload="none" poster="../../assets/lulu-ellie/original-adventure/book-20/front-cover.jpg"><source src="../../assets/lulu-ellie/original-adventure/book-20/animated-cover.mp4" type="video/mp4">Your browser does not support the animated cover preview.</video></aside></div></section>
      <section><div class="site-shell section-card"><div class="section-head"><div class="section-kicker">Archive status</div><h2>Twenty full books, with marketplace claims handled separately.</h2><p class="section-lede">The archive confirms the books and matching media. Purchase links appear only where the public marketplace record supports them.</p></div><div class="card-grid"><article class="card"><h3>Books 1–20</h3><p>Source-confirmed full books in canonical order.</p></article><article class="card"><h3>Number-aligned media</h3><p>Cover, motion, and feature media remain mapped Book 1 through Book 20.</p></article><article class="card"><h3>Motion controls</h3><p>Archive videos are created and loaded only after a visitor selects a cover.</p></article><article class="card"><h3>Reduced motion</h3><p>Automatic motion pauses when reduced motion is requested.</p></article></div></div></section>
      <section id="named-books"><div class="site-shell section-card"><div class="section-head"><div class="section-kicker">Canonical storybooks</div><h2>Original Adventure Books 1–20</h2></div><ol class="bullets">{lis}</ol><div id="named-media-grid" class="book-media-grid" aria-label="Original Adventure media"></div></div></section>
      <section id="feature-pages"><div class="site-shell section-card"><div class="section-head"><div class="section-kicker">Interior feature pages</div><h2>Story-world details from the archive.</h2></div><div id="feature-media-grid" class="book-media-grid" aria-label="Original Adventure interior feature media"></div></div></section>
    </main>
    {footer("../../")}
  </body>
</html>
"""
    js_items = ",\n    ".join(
        "{ number: %d, title: %s, slug: %s, cover: %s }" % (
            int(book["number"]), json.dumps(book["title"]), json.dumps(book["slug"] + ".html"), json.dumps("png" if int(book["number"]) == 1 else "jpg")
        )
        for book in books
    )
    js = f"""(() => {{
  "use strict";
  const namedBooks = [
    {js_items}
  ];
  const assetRoot = "../../assets/lulu-ellie/original-adventure";
  const imageRoot = "/web-image/assets/lulu-ellie/original-adventure";
  const make = (tag, className, text) => {{ const e = document.createElement(tag); if (className) e.className = className; if (text) e.textContent = text; return e; }};
  const coverUrl = (item) => `${{assetRoot}}/book-${{item.number}}/front-cover.${{item.cover}}`;
  const videoUrl = (item) => `${{assetRoot}}/book-${{item.number}}/animated-cover.mp4`;
  const loadablePreview = (item) => {{
    const button = make("button", "media-load-button"); button.type = "button"; button.setAttribute("aria-label", `Load motion preview for ${{item.title}}`);
    const image = document.createElement("img"); image.src = coverUrl(item); image.alt = `${{item.title}} cover art`; image.loading = "lazy"; image.decoding = "async"; image.fetchPriority = "low";
    const label = make("span", "media-load-label", "Load motion preview"); button.append(image, label);
    button.addEventListener("click", () => {{ const video = document.createElement("video"); video.controls = true; video.muted = true; video.loop = true; video.playsInline = true; video.preload = "metadata"; video.poster = coverUrl(item); video.setAttribute("aria-label", `Motion preview for ${{item.title}}`); const source = document.createElement("source"); source.src = videoUrl(item); source.type = "video/mp4"; video.append(source, document.createTextNode("Your browser does not support the animated cover preview.")); button.replaceWith(video); video.load(); const p = video.play(); if (p && typeof p.catch === "function") p.catch(() => undefined); }}, {{ once: true }});
    return button;
  }};
  const mediaCard = (item) => {{ const article = make("article", "card book-media-card"); const copy = make("div", "card-copy"); const tags = make("div", "tag-row"); tags.append(make("span", "book-number", `Book ${{item.number}}`), make("span", "status-badge", "Named storybook")); copy.append(tags, make("h3", "", item.title), make("p", "", "Cover art and optional motion preview from the matching numbered archive folder.")); const actions = make("div", "section-actions"); const link = make("a", "button ghost", "Explore Book"); link.href = `../../books/${{item.slug}}`; actions.append(link); copy.append(actions); article.append(loadablePreview(item), copy); return article; }};
  const featureCard = (item) => {{ const article = make("article", "card book-media-card"); const image = document.createElement("img"); image.src = `${{assetRoot}}/book-${{item.number}}/feature-page.png`; image.alt = `${{item.title}} interior feature page`; image.loading = "lazy"; image.decoding = "async"; image.fetchPriority = "low"; const copy = make("div", "card-copy"); const tags = make("div", "tag-row"); tags.append(make("span", "book-number", `Book ${{item.number}}`), make("span", "status-badge", "Interior media")); copy.append(tags, make("h3", "", item.title), make("p", "", "Interior feature art preserved in the numbered media archive.")); article.append(image, copy); return article; }};
  const namedRoot = document.getElementById("named-media-grid"); const featureRoot = document.getElementById("feature-media-grid");
  namedBooks.forEach((item) => namedRoot?.append(mediaCard(item))); namedBooks.filter((item) => item.number >= 2).forEach((item) => featureRoot?.append(featureCard(item)));
}})();
"""
    return page, js


def mystery_books(master: dict) -> list[dict]:
    series = next(s for s in master["series"] if s["id"] == "mystery-tails")
    titles = series.get("source_confirmed_titles", {})
    return [
        {"number": int(n), "title": title, "slug": re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")}
        for n, title in sorted(titles.items(), key=lambda item: int(item[0])) if int(n) <= 5
    ]


def render_mystery_page(book: dict) -> str:
    title = book["title"]; n = book["number"]; prefix = "../"
    description = f"{title} is a source-confirmed Lulu & Ellie Mystery Tails book. Current marketplace status is unverified."
    return f"""<!doctype html><html lang="en" data-nav="library">
{head(title + " | Lulu & Ellie Mystery Tails", description, prefix)}
<body data-nav="library">{header(prefix, "library")}<main id="main">
<section class="page-hero"><div class="site-shell hero-grid"><article class="hero-panel"><div class="eyebrow">Lulu &amp; Ellie Mystery Tails · Book {n}</div><h1>{esc(title)}</h1><p class="lede">A source-confirmed full book in the Mystery Tails collection.</p><p class="support-note">Synopsis, release claims, and marketplace links are intentionally withheld until the public catalog review is complete.</p></article><aside class="hero-side"><div class="portal-card"><div class="portal-top"><div><div class="eyebrow">Catalog status</div><div class="portal-title">Source-confirmed preview</div></div><span class="status-badge">Marketplace unverified</span></div><p class="portal-copy">The full source book is archived. This page does not claim a price, release date, or current orderability.</p></div></aside></div></section>
<section><div class="site-shell section-card"><div class="section-head"><div class="section-kicker">Explore More</div><h2>Continue through Mystery Tails.</h2></div><div class="section-actions"><a class="button" href="../series/mystery-tails.html">Back to Mystery Tails</a><a class="button secondary" href="../library.html">Full Library</a></div></div></section>
</main>{footer(prefix)}</body></html>"""


def render_mystery_series(master: dict) -> str:
    books = mystery_books(master)
    cards = "".join(f'<article class="book-list-card"><div class="tag-row"><span class="book-number">Book {b["number"]}</span><span class="status-badge">Source-confirmed preview</span></div><h3>{esc(b["title"])}</h3><p>Full source book archived; marketplace status unverified.</p><div class="section-actions"><a class="button ghost" href="../books/{b["slug"]}.html">Explore Book</a></div></article>' for b in books)
    return f"""<!doctype html><html lang="en" data-nav="library">
{head("Lulu & Ellie Mystery Tails | Cozy Mystery Series", "Source-confirmed Mystery Tails books, with marketplace and release claims kept separate from archive evidence.", "../")}
<body data-nav="library">{header("../", "library")}<main id="main">
<section class="page-hero"><div class="site-shell hero-grid"><article class="hero-panel"><div class="eyebrow">Cozy mystery series</div><h1>Lulu &amp; Ellie Mystery Tails</h1><p class="lede">Gentle clue-following mysteries with a source-backed public catalog.</p><p class="support-note">The first five source-confirmed titles replace earlier concept-preview titles that did not match the archived books.</p></article><aside class="hero-side"><div class="portal-card"><div class="portal-top"><div><div class="eyebrow">Catalog status</div><div class="portal-title">Source-backed preview</div></div><span class="status-badge">In the works</span></div><p class="portal-copy">Marketplace availability is not inferred from the existence of a full source book.</p></div></aside></div></section>
<section id="books"><div class="site-shell section-card"><div class="section-head"><div class="section-kicker">Source-confirmed titles</div><h2>Mystery Tails Books 1–5</h2><p class="section-lede">These titles are aligned to the archived source books. Additional archived volumes remain out of the public title list until their catalog details are reconciled.</p></div><div class="book-list-grid">{cards}</div></div></section>
</main>{footer("../")}</body></html>"""


def render_source_status_series(master: dict, series_id: str, eyebrow: str, lede: str) -> str:
    series = next(s for s in master["series"] if s["id"] == series_id)
    count = len(series.get("complete_books", []))
    name = series["name"]
    description = f"{name} is a source-backed Lulu & Ellie collection. {count} full source book" + (" is" if count == 1 else "s are") + " archived while the public catalog is reconciled."
    return f"""<!doctype html><html lang="en" data-nav="library">
{head(name + " | Lulu & Ellie", description, "../")}
<body data-nav="library">{header("../", "library")}<main id="main">
<section class="page-hero"><div class="site-shell hero-grid"><article class="hero-panel"><div class="eyebrow">{esc(eyebrow)}</div><h1>{esc(name)}</h1><p class="lede">{esc(lede)}</p><p class="support-note">Source-backed preview: {count} full source book{" is" if count == 1 else "s are"} archived. Individual public titles, release claims, and marketplace links stay withheld until the title-by-title catalog review is complete.</p></article><aside class="hero-side"><div class="portal-card"><div class="portal-top"><div><div class="eyebrow">Catalog status</div><div class="portal-title">Archive verified · public catalog reconciling</div></div><span class="status-badge">Intentional preview</span></div><p class="portal-copy">Source-file existence confirms the developed books. It does not, by itself, prove a current public release, price, or orderability.</p></div></aside></div></section>
<section><div class="site-shell section-card"><div class="section-head"><div class="section-kicker">Source Status</div><h2>{count} full source book{" is" if count == 1 else "s are"} archived.</h2><p class="section-lede">This series page deliberately avoids old concept titles while the canonical public catalog is being reconciled against the archive.</p></div><div class="section-actions"><a class="button" href="../library.html">Full Library</a><a class="button secondary" href="../lulu-ellie/">Lulu &amp; Ellie Hub</a><a class="button secondary" href="../contact.html">Contact Dark Star</a></div></div></section>
</main>{footer("../")}</body></html>"""


def render_time_tails(master: dict) -> str:
    return render_source_status_series(
        master,
        "time-tails",
        "Time-adventure series",
        "A time-bending Lulu & Ellie series where clocks, seeds, promises, and tomorrow-sized mysteries open new paths.",
    )


def render_library(master: dict) -> str:
    original = original_series(master)
    book_cards = "".join(f'<article class="book-list-card"><div class="tag-row"><span class="book-number">Book {b["number"]}</span><span class="status-badge">Book</span></div><h3>{esc(b["title"])}</h3><p>Canonical Original Adventure Book {b["number"]}.</p><div class="section-actions"><a class="button ghost" href="books/{b["slug"]}.html">Explore Book</a></div></article>' for b in original["books"])
    series_cards = [
        ("Lulu & Ellie Adventures","Flagship storyworld","Twenty source-confirmed Original Adventure books.","series/lulu-and-ellie-adventures.html"),
        ("Lulu & Ellie Mystery Tails","Source-backed preview","Canonical source titles are being restored to the public catalog.","series/mystery-tails.html"),
        ("Lulu & Ellie Creature Rescue Club","In the works","Warm magical-creature rescue adventures.","series/creature-rescue-club.html"),
        ("Lulu & Ellie Backyard Academy","In the works","Nature, science, and discovery adventures.","series/backyard-academy.html"),
        ("Lulu & Ellie Go To Camp","In the works","Campfire-cozy adventures about teamwork and trying new things.","series/go-to-camp.html"),
        ("Lulu & Ellie in Space","In the works","Cozy space-rescue adventures across friendly worlds.","series/lulu-and-ellie-in-space.html"),
        ("Lulu & Ellie Time Tails","In the works","Time-bending adventures joining the public library architecture.","series/time-tails.html"),
        ("Lulu & Ellie Bedtime Adventures","Coming soon","Soft, low-stimulation bedtime stories.","series/bedtime-adventures.html"),
    ]
    series_html = "".join(f'<article class="mini-card"><div class="tag-row"><span class="tag">Storybook series</span><span class="status">{esc(status)}</span></div><h3>{esc(name)}</h3><p>{esc(desc)}</p><a class="button ghost" href="{href}">Explore</a></article>' for name,status,desc,href in series_cards)
    learning_cards = "".join([
        '<article class="mini-card"><h3>Lulu &amp; Ellie Phonics Path</h3><p>Early-reading practice for letters, sounds, blending, and short vowels.</p><a class="button ghost" href="learning/phonics-path.html">Explore</a></article>',
        '<article class="mini-card"><h3>Lulu &amp; Ellie Write &amp; Wag</h3><p>Handwriting practice from first letters through complete sentences.</p><a class="button ghost" href="learning/write-and-wag.html">Explore</a></article>',
        '<article class="mini-card"><h3>Lulu &amp; Ellie Cursive Club</h3><p>Cursive practice through notes, clues, and adventure words.</p><a class="button ghost" href="learning/cursive-club.html">Explore</a></article>',
        '<article class="mini-card"><h3>Lulu &amp; Ellie Learning Club</h3><p>Story-powered early learning, reading, and math practice.</p><a class="button ghost" href="learning/learning-club.html">Explore</a></article>',
        '<article class="mini-card"><h3>Companion &amp; Activity Library</h3><p>Adventure logs, field guides, keepsakes, puzzles, coloring, cookbooks, bedtime books, and more.</p><a class="button ghost" href="companion-library.html">Explore</a></article>',
    ])
    return f"""<!doctype html><html lang="en">
{head("The Lulu & Ellie Library | Series, Learning Lines & Books", "The Lulu & Ellie Library brings together the canonical Original Adventure sequence, storybook series, learning lines, and companion collections.", "")}
<body>{header("", "library")}<main id="main">
<section class="page-hero"><div class="site-shell hero-grid"><article class="hero-panel"><div class="eyebrow">The Lulu &amp; Ellie Library</div><h1>One library, with one source of truth.</h1><p class="lede">Storybook series, learning lines, companion books, and the complete twenty-book Original Adventure sequence.</p><p class="lede">Book existence, public announcement state, and marketplace availability are tracked separately so the catalog stays useful without making unsupported claims.</p><div class="hero-actions"><a class="button" href="#all-books">Original Adventure Books 1–20</a><a class="button secondary" href="companion-library.html">Companion Library</a></div></article><aside class="tier-hero-media"><img src="assets/lulu-ellie/original-adventure/book-20/front-cover.jpg" alt="Lulu &amp; Ellie and the Keeper Ring cover art" loading="eager" decoding="async"></aside></div></section>
<section id="storybook-series"><div class="site-shell section-card"><div class="section-head"><div class="section-kicker">Storybook Series</div><h2>Choose a storyworld.</h2></div><div class="mini-grid">{series_html}</div></div></section>
<section><div class="site-shell section-card"><div class="section-head"><div class="section-kicker">Learning &amp; Companion Lines</div><h2>Practice, play, make, and explore.</h2></div><div class="mini-grid">{learning_cards}</div></div></section>
<section id="all-books"><div class="site-shell section-card"><div class="section-head"><div class="section-kicker">Canonical Original Adventure</div><h2>Books 1–20</h2><p class="section-lede">These book numbers follow canonical story order. Marketplace links, where recorded, live on the individual book pages and remain subject to current verification.</p></div><div class="book-list-grid">{book_cards}</div></div></section>
</main>{footer("")}</body></html>"""


def redirect_page(title: str, target: str, prefix: str = "../") -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0; url={esc(target)}"><title>{esc(title)}</title><link rel="canonical" href="{esc(target)}"><link rel="stylesheet" href="{prefix}styles.css"></head><body><main id="main"><section class="page-hero"><div class="site-shell section-card"><h1>{esc(title)}</h1><p class="section-lede">This concept-preview page has moved to the source-backed series catalog.</p><a class="button" href="{esc(target)}">Open current series page</a></div></section></main></body></html>"""


def patch_all_html(master: dict) -> None:
    canonical_original = {b["slug"] + ".html" for b in original_series(master)["books"]}
    canonical_mystery = {b["slug"] + ".html" for b in mystery_books(master)}
    for page in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", ".github"} for part in page.parts):
            continue
        text = page.read_text(encoding="utf-8")
        if "http-equiv=\"refresh\"" in text.lower() or "http-equiv='refresh'" in text.lower():
            continue
        prefix = root_prefix(page)
        relative_name = page.relative_to(ROOT).as_posix()
        text = text.replace("series/lulu-and-ellie-adventures.html#purchase", "series/lulu-and-ellie-adventures.html#marketplace-links")
        text = text.replace("../series/lulu-and-ellie-adventures.html#purchase", "../series/lulu-and-ellie-adventures.html#marketplace-links")
        if relative_name in {"index.html", "agency.html", "ambrose-caspian-vale.html", "parents-teachers.html"} and "hero-brand-art" not in text and '<aside class="hero-side">' in text:
            art_number = 1 if relative_name != "agency.html" else 20
            art_ext = "png" if art_number == 1 else "jpg"
            art_title = "Lulu & Ellie and the Secret of Blackwater Bay" if art_number == 1 else "Lulu & Ellie and the Keeper Ring"
            art = f'<figure class="hero-brand-art"><img src="{prefix}assets/lulu-ellie/original-adventure/book-{art_number}/front-cover.{art_ext}" alt="{art_title} cover art" loading="eager" decoding="async"></figure>'
            text = text.replace("</aside>", art + "</aside>", 1)
        if "favicon.svg" not in text and "</head>" in text.lower():
            text = re.sub(r"\s*</head>", f'\n    <link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">\n  </head>', text, count=1, flags=re.I)
        if "accessibility.css" not in text and "</head>" in text.lower():
            text = re.sub(r"\s*</head>", f'\n    <link rel="stylesheet" href="{prefix}accessibility.css">\n  </head>', text, count=1, flags=re.I)
        footer_match = re.search(r'(<footer class="site-footer">.*?<div class="site-shell footer-inner">)(.*?)(</div>\s*</footer>)', text, re.I | re.S)
        if footer_match and "accessibility.html" not in footer_match.group(0):
            replacement = footer_match.group(1) + footer_match.group(2) + f'\n        <div><a href="{prefix}accessibility.html">Accessibility</a></div>\n      ' + footer_match.group(3)
            text = text[:footer_match.start()] + replacement + text[footer_match.end():]
        def optimize_public_image(match: re.Match[str]) -> str:
            attribute = match.group(1)
            source = match.group(2)
            if source.startswith("/web-image/") or source.startswith("http://") or source.startswith("https://") or source.startswith("data:"):
                return match.group(0)
            source_path = (ROOT / source.lstrip("/")) if source.startswith("/") else (page.parent / source)
            try:
                relative_asset = source_path.resolve().relative_to(ROOT.resolve()).as_posix()
            except ValueError:
                return match.group(0)
            if not relative_asset.startswith("assets/"):
                return match.group(0)
            return f'{attribute}="/web-image/{relative_asset}"'

        text = re.sub(
            r'\\b(src|poster)=["\\']([^"\\']+\\.(?:png|jpe?g|webp))["\\']',
            optimize_public_image,
            text,
            flags=re.I,
        )

        if page.parent.name == "books":
            name = page.name
            if name not in canonical_original and name not in canonical_mystery and "http-equiv=\"refresh\"" not in text.lower():
                if 'name="robots"' not in text:
                    text = re.sub(r"\s*</head>", '\n    <meta name="robots" content="noindex,follow">\n  </head>', text, count=1, flags=re.I)
                if "catalog-notice" not in text:
                    notice = '<div class="site-shell catalog-notice" role="note"><strong>Concept preview.</strong> This page is not being treated as a canonical source-book record while the public catalog is reconciled with the full Lulu &amp; Ellie archive.</div>'
                    text = text.replace('<main id="main">', '<main id="main">' + notice, 1)
        page.write_text(text, encoding="utf-8")


def write_site() -> None:
    master = load_json(MASTER)
    market = marketplace_map()
    books = original_series(master)["books"]
    for book in books:
        if int(book["number"]) >= 11:
            (ROOT / "books" / f'{book["slug"]}.html').write_text(original_book_page(book, books), encoding="utf-8")
    book10 = ROOT / "books" / "lulu-and-ellie-and-the-star-map-of-everywhere.html"
    if book10.is_file():
        text = book10.read_text(encoding="utf-8")
        if "Next: Book 11" not in text:
            text = text.replace('<a class="button" href="../series/lulu-and-ellie-adventures.html">Back to Series</a>', '<a class="button" href="../series/lulu-and-ellie-adventures.html">Back to Series</a><a class="button secondary" href="../books/lulu-and-ellie-and-the-lanterns-of-firefly-hollow.html">Next: Book 11</a>', 1)
            text = text.replace("The first ten-book arc is complete.", "The Original Adventure continues through Book 20.")
            book10.write_text(text, encoding="utf-8")
    (ROOT / "series" / "lulu-and-ellie-adventures.html").write_text(render_original_series(master, market), encoding="utf-8")
    archive_page, archive_js = render_archive(master)
    (ROOT / "lulu-ellie" / "original-adventure" / "index.html").write_text(archive_page, encoding="utf-8")
    (ROOT / "lulu-ellie" / "original-adventure" / "archive.js").write_text(archive_js, encoding="utf-8")
    (ROOT / "library.html").write_text(render_library(master), encoding="utf-8")
    (ROOT / "series" / "mystery-tails.html").write_text(render_mystery_series(master), encoding="utf-8")
    for book in mystery_books(master):
        (ROOT / "books" / f'{book["slug"]}.html').write_text(render_mystery_page(book), encoding="utf-8")
    (ROOT / "series" / "time-tails.html").write_text(render_time_tails(master), encoding="utf-8")
    source_status_pages = {
        "lulu-and-ellie-in-space.html": ("in-space", "Space rescue series", "Cozy space-rescue adventures across friendly worlds."),
        "creature-rescue-club.html": ("creature-rescue-club", "Creature rescue series", "Warm rescue adventures about noticing what magical creatures need and helping them find safety."),
        "go-to-camp.html": ("go-to-camp", "Camp adventure series", "Campfire-cozy adventures about teamwork, trying new things, and gentle outdoor mysteries."),
        "backyard-academy.html": ("backyard-academy", "Nature learning storybooks", "Nature, science, and discovery adventures built around curiosity and careful observation."),
        "bedtime-adventures.html": ("bedtime-adventures", "Bedtime storybooks", "Soft, low-stimulation bedtime stories with quiet wonder and calm endings."),
    }
    for filename, (series_id, eyebrow, lede) in source_status_pages.items():
        (ROOT / "series" / filename).write_text(
            render_source_status_series(master, series_id, eyebrow, lede),
            encoding="utf-8",
        )
    stale_mystery = {
        "mystery-tails-the-case-of-the-missing-mooncake.html": "Moved: The Case of the Missing Mooncake",
        "mystery-tails-the-lighthouse-that-blinked-twice.html": "Moved: The Lighthouse That Blinked Twice",
        "mystery-tails-the-pawprints-in-the-pumpkin-patch.html": "Moved: The Pawprints in the Pumpkin Patch",
    }
    for stale, title in stale_mystery.items():
        path = ROOT / "books" / stale
        if path.exists():
            path.write_text(redirect_page(title, "../series/mystery-tails.html"), encoding="utf-8")
    patch_all_html(master)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("choose exactly one of --write or --check")
    if args.write:
        write_site()
        print("Reconciled public catalog from data/library-master.json")
        return 0
    before = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8") for p in ROOT.rglob("*.html")}
    before_js = (ROOT / "lulu-ellie" / "original-adventure" / "archive.js").read_text(encoding="utf-8")
    write_site()
    changed = [path for path, old in before.items() if (ROOT / path).read_text(encoding="utf-8") != old]
    after_js = (ROOT / "lulu-ellie" / "original-adventure" / "archive.js").read_text(encoding="utf-8")
    if after_js != before_js:
        changed.append("lulu-ellie/original-adventure/archive.js")
    if changed:
        print("Catalog reconciliation is not current. Run: python scripts/reconcile_catalog.py --write")
        for path in sorted(changed):
            print(f"- {path}")
        return 1
    print("Catalog reconciliation is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
