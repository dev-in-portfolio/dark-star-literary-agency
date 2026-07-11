# Dark Star Literary Agency Site Blueprint

## Public Architecture

- `index.html` — agency gateway
- `agency.html` — Dark Star identity
- `ambrose-caspian-vale.html` — author identity
- `lulu-ellie/` — flagship Lulu & Ellie universe hub
- `lulu-ellie/original-adventure/` — 20-volume media archive with ten named storybooks and ten archive-preview volumes
- `library.html` — growing public library
- `companion-library.html` — source-backed companion catalog
- `parents-teachers.html` — trust and educational-use page
- `accessibility.html` — public accessibility statement and feedback route
- `contact.html` — agency contact page

The legacy `/lulu-and-ellie.html` route redirects permanently to `/lulu-ellie/`.

## Catalog Model

The public site separates:

1. Named and documented storybooks
2. Clearly labeled media previews
3. Developed companion interiors
4. Marketplace verification state
5. Accessibility release state

The existence of source media or an interior file is not treated as proof of publication, purchase availability, or accessible digital-release readiness.

## Companion Source Controls

- `data/companion-catalog.json` represents the public companion catalog.
- `data/companion-source-manifest.csv` records exact source package, internal PDF path, page count, SHA-256, quality status, and marketplace status.
- `data/pdf-accessibility-audit.json` records text-layer, tagging, reading-order, alternative-text, language, remediation, and release state for the same 44 source IDs.
- Raw source PDFs remain outside the public website repository.

## Marketplace Controls

- `data/marketplace-records.json` stores recorded Amazon links and verification state for canonical Books 1–10.
- A recorded ASIN is not proof of current price, format, stock, or orderability.
- Book 6 remains in a no-active-link state until manually verified.

## Media Controls

- `data/media-inventory.json` records public-media paths, sizes, types, and SHA-256 values.
- `data/media-budget.json` limits aggregate and per-file growth.
- Original Adventure archive videos are click-to-load.
- Automatic previews use `preload="none"`, visibility-aware playback, and reduced-motion safeguards.

## SEO and Discovery

- `data/site-config.json` centralizes the production URL, site identity, locale, author identity, series identity, contact email, and social defaults.
- `scripts/update_seo.py` generates canonical and social metadata, `robots.txt`, and `sitemap.xml`.
- `scripts/update_structured_data.py` generates conservative homepage and canonical-book JSON-LD.
- `accessibility.html` is canonicalized and included in the sitemap.

## Accessibility Direction

The website uses skip links, semantic headings, visible focus, image alternatives, controlled media, and reduced-motion support.

The 44 supplied companion PDFs are image-based source files. The July 11, 2026 baseline found no usable extractable text. They remain blocked from accessible digital distribution until text, semantic tags, reading order, meaningful alternatives, language metadata, manual assistive-technology QA, and an exact release-file checksum are verified.

The public accessibility statement:

- Describes current website features
- Discloses known source-PDF limitations
- Explains third-party boundaries
- Provides a direct barrier-reporting and accessible-format request route
- Avoids claiming blanket formal conformance

## Design Direction

- Midnight navy and black-blue background
- Soft gold accents
- Ivory text
- Subtle star and portal glow
- Premium literary styling with warmer child-friendly accents inside Lulu & Ellie content
- Motion previews that respect reduced-motion preferences and do not all play simultaneously

## Technical Direction

Run all seven release checks before deployment:

1. `validate_site.py`
2. `validate_source_manifest.py`
3. `validate_marketplace.py`
4. `update_seo.py --check`
5. `update_structured_data.py --check`
6. `update_media_inventory.py --check`
7. `validate_pdf_accessibility.py`

Keep book numbers, titles, page slugs, Previous/Next links, media directories, source hashes, marketplace records, and accessibility records aligned. Keep source archives and production interiors outside the website repository.

## Public Positioning

The site should feel polished, literary, and magical immediately. Future collections remain hidden unless they are purchase-ready, preorder-ready, sample-ready, or intentionally announced as clearly labeled previews. Unapproved source PDFs must not be linked or described as accessible digital editions.
