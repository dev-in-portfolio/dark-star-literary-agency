# Dark Star Literary Agency

Static multi-page public website for Dark Star Literary Agency, the creative home of Ambrose Caspian Vale and the Lulu & Ellie Adventures.

## Current Site Structure

- `index.html` - homepage and brand gateway
- `agency.html` - Dark Star Literary Agency identity page
- `ambrose-caspian-vale.html` - author page
- `lulu-ellie/` - current Lulu & Ellie flagship-universe hub
- `lulu-ellie/original-adventure/` - 20-volume Original Adventure media archive with ten named storybooks and ten archive-preview volumes
- `lulu-and-ellie.html` - legacy redirect to the current Lulu & Ellie hub
- `library.html` - live, growing library landing and navigation hub
- `companion-library.html` - source-backed static preview of activity, learning, keepsake, puzzle, coloring, cookbook, and bedtime collections
- `parents-teachers.html` - parent and teacher trust page
- `contact.html` - public contact page

### Series Pages

- `series/lulu-and-ellie-adventures.html`
- `series/mystery-tails.html`
- `series/creature-rescue-club.html`
- `series/backyard-academy.html`
- `series/go-to-camp.html`
- `series/lulu-and-ellie-in-space.html`
- `series/bedtime-adventures.html`

### Learning Pages

- `learning/phonics-path.html`
- `learning/write-and-wag.html`
- `learning/cursive-club.html`
- `learning/learning-club.html`

### Book Pages

- `books/` contains the public catalog's individual book pages.
- Original Adventure Books 1-10 use canonical story order rather than Amazon publication or listing order.
- Recorded Amazon ASIN links may be shown, but current price, format, stock, and orderability must be confirmed on Amazon.
- Book 6 does not expose an Amazon product link while no current listing has been manually verified.
- Intentionally announced previews must use clear `Coming Soon`, `In the Works`, or `Preview` language and must not imply availability.

## Companion Catalog

The Companion Library uses:

- `data/companion-catalog.json` - structured public catalog
- `data/companion-source-manifest.csv` - exact source ZIP, internal PDF path, page count, SHA-256, readiness status, marketplace status, and review date
- `companion-library.html` - complete static catalog markup
- `companion-library.js` - runtime consistency check only; it does not replace the static catalog

It currently represents:

- 44 supplied PDF interiors
- 12 public collection groups
- Activity logs, handwriting, cursive, phonics, learning, field guides, keepsakes, diaries, search-and-find, puzzles, coloring books, cookbooks, and bedtime stories

The underlying source PDFs remain production assets and are not duplicated into this repository. A completed interior proves that a title exists as a developed source file; it does not by itself prove that the title is publication-ready or currently available for purchase.

See `docs/source-catalog-inventory.md` for the source-package inventory.

## Media Source Repository

The organized Lulu & Ellie media source is:

- `dev-in-portfolio/l_e_storage`
- Default branch: `l_e_storage`

It contains the Original Adventure Book 1-20 cover, feature or fun-page, and MP4 mappings plus shared General media. The website preserves a strict number-to-number relationship between storage `Book_#` folders and website `book-#` folders.

See `docs/storage-integration.md` for the mapping and media policy.

## Shared Presentation

- `styles.css` contains the main layout, color palette, cards, buttons, badges, book layouts, archive layouts, and responsive behavior.
- `accessibility.css` adds reduced-motion safeguards for media-rich pages and the live Library.
- `media.js` keeps automatic videos at `preload="none"`, allows only the most visible preview to play, and pauses managed media when the page is hidden or reduced motion is requested.
- `lulu-ellie/original-adventure/archive.js` creates archive video elements only after a visitor explicitly selects a cover.

## Validation

Run all repository checks before publishing:

```bash
python scripts/validate_site.py
python scripts/validate_source_manifest.py
python scripts/validate_marketplace.py
python scripts/update_seo.py --check
python scripts/update_structured_data.py --check
python scripts/update_media_inventory.py --check
python scripts/validate_pdf_accessibility.py
```

The checks cover:

- Broken local links and missing assets
- Missing page titles, descriptions, primary headings, and duplicate element IDs
- Missing image alt text and unsafe autoplay video markup
- Redirect-page canonical targets
- Original Adventure cover, animation, and feature-page mapping for Books 1-20
- Canonical book numbers, media folders, and Previous/Next navigation for Books 1-10
- Correct archive wording for preview Volumes 11-20
- Companion catalog structure, 12 collection groups, 44 unique titles, and valid page counts
- Exact reconciliation among the public catalog, static `data-source-id` entries, and the checksum-backed source manifest
- Evidence-based marketplace wording, recorded ASIN preservation, and the no-link state for Book 6
- The Library's `Growing library` status and current marketplace explanation
- Absolute canonical URLs, Open Graph URLs, social-card metadata, `robots.txt`, and `sitemap.xml` consistency
- Organization, author, website, and canonical Book JSON-LD consistency
- Exact media paths, sizes, checksums, aggregate budgets, per-file budgets, and deferred-delivery behavior
- Exact reconciliation of all 44 PDF accessibility records with source filenames, page counts, and SHA-256 values
- Prevention of public PDF links and accessible-edition claims until remediation is approved

GitHub Actions compiles and runs seven permanent checks: the three content validators, SEO, structured data, media inventory, and PDF accessibility release validation on pull requests and pushes to `main` or `agent/**`. It uploads a combined validation report even when a future run fails.

## SEO and Discoverability

- `data/site-config.json` is the single source for the public site name, production base URL, locale, contact email, author identity, series identity, and Twitter card defaults.
- The current production base URL is `https://dark-star-literary-agency.netlify.app`.
- `scripts/update_seo.py --write` generates or refreshes absolute canonical URLs, `og:url`, `og:site_name`, `og:locale`, Twitter card metadata, image-based Open Graph tags where a real local image exists, `robots.txt`, and `sitemap.xml`.
- `scripts/update_structured_data.py --write` generates conservative JSON-LD for the homepage organization, author, and website identities plus the ten canonical Original Adventure storybooks.
- Book JSON-LD intentionally omits prices, offers, stock, format availability, and unverified Amazon claims.
- Redirect pages point their canonical URL at the destination and are excluded from the sitemap.
- Both generator scripts support `--check` and fail when generated output drifts from the configuration or marketplace registry.
- To adopt a future custom domain, change `site_url` once in `data/site-config.json`, run both writers, review the generated diff, and commit the result.

## Public Media Inventory and Budgets

The checked-in public media baseline is recorded in `data/media-inventory.json`:

- 59 public media files
- 287,757,879 bytes total
- 39 images using 156,340,193 bytes
- 20 MP4 files using 131,417,686 bytes
- Largest image: 12,710,158 bytes
- Largest video: 8,532,841 bytes

`data/media-budget.json` limits the repository to:

- 300,000,000 total public-media bytes
- 165,000,000 image bytes
- 140,000,000 video bytes
- 13,000,000 bytes per image
- 9,000,000 bytes per video

Any intentional asset change requires regenerating the inventory with `python scripts/update_media_inventory.py --write`, reviewing the checksum and size diff, and staying within or explicitly revising the budgets.

The Original Adventure archive uses lazy low-priority cover images and creates each controlled MP4 only after selection. Automatic previews use `preload="none"` and are managed by viewport and reduced-motion rules.

## PDF Accessibility Baseline

`data/pdf-accessibility-audit.json` records the July 11, 2026 baseline for all 44 supplied companion interiors. The audit found no usable extractable text in the source PDFs, so every source file remains blocked from accessible digital distribution until remediation is manually verified.

`scripts/validate_pdf_accessibility.py` checks source IDs, filenames, page counts, SHA-256 values, remediation states, approval requirements, and public PDF links. A record cannot be approved unless text, semantic tags, reading order, meaningful alternatives, language metadata, and manual QA are verified.

See `docs/pdf-accessibility-remediation.md` for the required workflow and `docs/pdf-accessibility-review-log-template.md` for the manual QA record.

## Deployment

`netlify.toml` defines:

- The static publish directory
- All three build-time content validators
- The generated SEO, sitemap, structured-data, media-inventory, and PDF-accessibility consistency checks
- The permanent legacy Lulu & Ellie redirect
- Baseline security headers
- Browser revalidation plus long-lived deploy-invalidated Netlify CDN caching for assets, CSS, and JavaScript

The latest draft-PR validation pass completed successfully in both GitHub Actions and the Netlify deploy preview. The PR remains unmerged until explicitly approved.

## Public Language

Use customer-facing terms such as:

- series
- collections
- book lines
- learning lines
- companion books
- library
- universe
- storyworld
- books
- adventures

Do not use internal production terms such as `branches` in public copy.

## Release and Preview Rules

Public navigation may contain:

1. Live catalog content with evidence-based marketplace or download information.
2. Preorder or sample-ready content with working official links.
3. Intentional preview pages that are clearly labeled and make no unsupported purchase or release-date claim.

Unapproved drafts, internal production pages, and unfinished downloads stay hidden.

## Marketplace Links

- The current Original Adventure pages preserve recorded Amazon ASIN links from existing publishing records.
- An ASIN link is not treated as proof of current price, format, stock, or orderability.
- Canonical book pages use `Amazon link on file`, `Current status unverified`, and `Check Amazon` wording until a manual review is recorded.
- Mushroom Moon Maze has no active Amazon product link while no current public listing is manually verified.
- Preview pages must not use active-looking placeholder purchase controls.
- Prefer non-interactive status text over `href="#"` placeholders.

## Media Handling

- Keep the media folder number aligned with the canonical public book number.
- Commit optimized public derivatives rather than production masters.
- Use poster images and fallback text for every animation.
- Keep automatic video loading at `preload="none"`.
- Use click-to-load controls for archive video collections.
- Avoid simultaneous autoplay; `media.js` manages viewport-aware playback on connected pages.
- Keep media inventory and budget files current.
- Use `l_e_storage` as the archive/source layer rather than duplicating its full media set into the website repository.

## Contact

Public contact email:

`darstarliteraryagency@gmail.com`
