# Dark Star Literary Agency Site Blueprint

## Public Architecture

- `index.html` — agency gateway
- `agency.html` — Dark Star identity
- `ambrose-caspian-vale.html` — author identity
- `lulu-ellie/` — flagship Lulu & Ellie universe hub
- `lulu-ellie/original-adventure/` — complete 20-book Original Adventure media archive
- `library.html` — canonical public library
- `companion-library.html` — source-backed companion catalog
- `parents-teachers.html` — parent / teacher trust page
- `accessibility.html` — accessibility statement and feedback route
- `contact.html` — public contact page

Series architecture includes Original Adventure, Mystery Tails, Creature Rescue Club, Backyard Academy, Go To Camp, In Space, Time Tails, and Bedtime Adventures.

## Catalog Model

`data/library-master.json` is the canonical public-catalog input.

The model deliberately separates:

1. source-book existence;
2. canonical title and sequence;
3. public catalog reconciliation state;
4. public visibility state;
5. marketplace evidence;
6. accessibility release state.

A PDF existing in storage is not proof that the title is currently for sale, available in a given format, or approved for accessible digital distribution.

## Storage Integration

The site recognizes seven authoritative storage repositories:

- `l_e_storage` — Original Adventure
- `l_e_storage2` — In Space
- `l_e_storage3` — Creature Rescue Club
- `l_e_storage4` — Mystery Tails + Time Tails
- `l_e_storage5` — Go To Camp
- `l_e_storage6` — learning library
- `l_e_storage7` — companion/activity library

See `docs/storage-integration.md`.

## Original Adventure

Original Adventure is fully reconciled at Books 1–20.

The site:

- preserves canonical story order;
- generates canonical pages for all 20;
- maps media Book 1 → book-1 through Book 20 → book-20;
- generates Book JSON-LD for all 20;
- keeps marketplace claims separate from archive status.

## Unreconciled Series

When a storage series is known but its public title-by-title catalog is not yet reconciled, the series page shows source-backed archive status without promoting old concept titles into canonical book records.

Legacy concept book pages are marked `noindex,follow` and visibly labeled as concept previews until they are either reconciled or redirected.

Mystery Tails Books 1–5 are currently source-title reconciled. Time Tails now exists in the public architecture as an intentional preview.

## Companion Source Controls

The existing 44-record companion catalog remains backed by:

- `data/companion-catalog.json`
- `data/companion-source-manifest.csv`
- `data/pdf-accessibility-audit.json`

Those records preserve exact provenance and accessibility release state independently of the broader storage-repository catalog.

## Marketplace Controls

`data/marketplace-records.json` preserves recorded Amazon evidence.

Marketplace links never prove current price, stock, format, or orderability. Unsupported prices and purchase claims are rejected by validation.

## SEO and Discovery

- `data/site-config.json` centralizes production URL and identity.
- `scripts/update_seo.py` generates canonical/social metadata and the sitemap.
- Local page art is preferred for social cards.
- `og-image.png` is the fallback social image.
- `noindex` preview pages are excluded from the sitemap.
- `favicon.svg` is the primary favicon.
- `scripts/update_structured_data.py` generates homepage identity data and Book data for all 20 canonical Original Adventure books.

## Accessibility and Interaction

Public pages use:

- skip links;
- semantic landmarks;
- visible keyboard focus;
- image alternatives;
- reduced-motion safeguards;
- safe new-tab behavior;
- explicit accessibility feedback routing.

The PDF accessibility registry remains a separate release gate for source interiors.

## Design Direction

- Midnight navy and black-blue foundation
- Soft gold accents
- Ivory text
- Subtle portal/star glow
- Real Lulu & Ellie cover art on core brand surfaces
- Premium literary styling with warm child-friendly art
- Horizontally scrollable compact navigation on narrower screens rather than a tall wrapped sticky header

## Release Architecture

GitHub Actions and Netlify both call:

```bash
python3 scripts/release_check.py
```

The command performs generation first and then runs the complete validation suite. There is no separate weaker Netlify release path.

## Public Positioning

The public site should feel like an intentional literary/publishing home, not an internal production dashboard.

Future titles may be represented publicly only when they are:

- canonical and intentionally announced;
- purchase-ready;
- preorder-ready;
- sample-ready; or
- deliberately presented as a clearly labeled preview.

Unsupported production notes, uncertain titles, and internal-only source material stay out of canonical public navigation.
