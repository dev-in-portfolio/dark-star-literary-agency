# Dark Star Literary Agency

Static multi-page public website for Dark Star Literary Agency, the creative home of Ambrose Caspian Vale and the Lulu & Ellie Adventures.

Production: `https://literaryagency.darkstarconsultinggroup.com`

## Canonical Catalog

`data/library-master.json` is the website's canonical Lulu & Ellie catalog source.

It records:

- the seven Lulu & Ellie storage repositories;
- series identity and source repository;
- expected, complete, and missing book numbers where the series numbering is established;
- canonical Original Adventure Books 1–20;
- public-state and catalog-reconciliation state;
- source-confirmed titles that may safely appear publicly.

Source-file existence, public announcement state, marketplace availability, price, and orderability are deliberately separate concepts.

## Storage Sources

| Repository | Collection |
|---|---|
| `dev-in-portfolio/l_e_storage` | Original Adventure |
| `dev-in-portfolio/l_e_storage2` | Lulu & Ellie in Space |
| `dev-in-portfolio/l_e_storage3` | Creature Rescue Club |
| `dev-in-portfolio/l_e_storage4` | Mystery Tails + Time Tails |
| `dev-in-portfolio/l_e_storage5` | Go To Camp |
| `dev-in-portfolio/l_e_storage6` | Academy / Learning / Phonics / Handwriting / Cursive |
| `dev-in-portfolio/l_e_storage7` | Companion & Activity Library |

The public site does not infer a marketplace claim merely because a full PDF exists in storage.

## Current Public Architecture

- `index.html` — agency gateway
- `agency.html` — Dark Star identity
- `ambrose-caspian-vale.html` — author identity
- `lulu-ellie/` — Lulu & Ellie universe hub
- `lulu-ellie/original-adventure/` — complete 20-book Original Adventure media archive
- `library.html` — canonical public library
- `companion-library.html` — source-backed companion catalog
- `parents-teachers.html` — parent and teacher trust page
- `accessibility.html` — public accessibility statement
- `contact.html` — public contact page

### Series Pages

- `series/lulu-and-ellie-adventures.html`
- `series/mystery-tails.html`
- `series/creature-rescue-club.html`
- `series/backyard-academy.html`
- `series/go-to-camp.html`
- `series/lulu-and-ellie-in-space.html`
- `series/time-tails.html`
- `series/bedtime-adventures.html`

Unreconciled series pages use conservative source-status previews instead of presenting old concept titles as canonical books.

### Learning Pages

- `learning/phonics-path.html`
- `learning/write-and-wag.html`
- `learning/cursive-club.html`
- `learning/learning-club.html`

## Original Adventure

All 20 full source books are archived and the public catalog follows canonical story order.

Books 1–10 retain the established richer pages and recorded marketplace evidence. Books 11–20 are generated from the canonical master catalog with the source-confirmed titles and matching numbered media.

Marketplace status remains separate. A stored full book does not create a purchase claim.

## Catalog Generation

`scripts/reconcile_catalog.py` deterministically generates or reconciles:

- the Library;
- Original Adventure series and Books 11–20;
- the complete Original Adventure media archive;
- source-backed Mystery Tails Books 1–5;
- the Time Tails series entry;
- conservative source-status pages for unreconciled series;
- cross-site accessibility/favicon/footer consistency;
- noindex treatment for legacy concept-preview book pages;
- corrected cross-page fragment links.

SEO, structured data, and media inventory are then regenerated from the reconciled site.

## Release Pipeline

Both GitHub Actions and Netlify execute the same command:

```bash
python3 scripts/release_check.py
```

That command:

1. reconciles the catalog;
2. regenerates SEO/social metadata;
3. regenerates structured data;
4. regenerates the media inventory;
5. validates the seven-source library master;
6. validates HTML, local links, local fragments, media mapping, and the 20-book sequence;
7. reconciles the 44-record companion source manifest;
8. validates marketplace evidence language;
9. validates generated SEO;
10. validates Book JSON-LD for all 20 Original Adventure books;
11. validates media inventory and deferred delivery;
12. validates the PDF accessibility registry;
13. validates keyboard/interaction semantics.

Production and CI therefore cannot intentionally use different release gates.

## SEO and Social

- Production canonical base: `https://literaryagency.darkstarconsultinggroup.com`
- `scripts/update_seo.py` generates canonical URLs, social metadata, robots.txt, and sitemap.xml.
- Pages with their own artwork use it for social sharing.
- Pages without a local image fall back to `og-image.png`.
- `noindex` concept-preview pages are excluded from the sitemap.
- `favicon.svg` is the primary Dark Star favicon.

## Marketplace Policy

`data/marketplace-records.json` preserves recorded Amazon evidence for Original Adventure Books 1–10.

A recorded ASIN or URL is not proof of current price, format, stock, or orderability. Public copy therefore uses evidence-aware wording such as:

- `Amazon link on file`
- `Current status unverified`
- `Check Amazon`

No fixed prices are published without a verification and refresh policy.

## Companion Catalog and PDF Accessibility

The Companion Library retains its exact 44-record source manifest and accessibility baseline.

A completed interior does not automatically mean that it is publication-ready or suitable for accessible digital distribution. The existing PDF accessibility registry remains the release gate for those source interiors.

## Media

The site maps Original Adventure Book 1–20 media number-for-number to the source archive.

Public pages use deferred video loading, lazy image loading, reduced-motion safeguards, and a checksum-backed media inventory. Production masters remain in the storage repositories rather than being duplicated into public catalog data.

## Redirects

Netlify provides permanent redirects for:

- `/lulu-and-ellie.html` → `/lulu-ellie/`
- `/books/lulu-and-ellie-and-the-lost-dinosaur-valley.html` → the canonical Lost Valley of Thunder page

## Public Language

Use public terms such as series, collections, book lines, learning lines, companion books, library, universe, storyworld, books, and adventures.

Do not expose internal production terminology as customer-facing catalog language.

## Contact

`literary@darkstarconsultinggroup.com`
