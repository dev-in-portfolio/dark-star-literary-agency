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
- `media.js` allows only the most visible automatic motion preview to play, preserves user-controlled videos, and pauses automatic media when the page is hidden or reduced motion is requested.

## Validation

Run all repository checks before publishing:

```bash
python scripts/validate_site.py
python scripts/validate_source_manifest.py
python scripts/validate_marketplace.py
python scripts/update_seo.py --check
python scripts/update_structured_data.py --check
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

GitHub Actions compiles and runs the three content validators plus the SEO and structured-data reproducibility checks on pull requests and pushes to `main` or `agent/**`. It uploads a combined validation report even when a future run fails.

## SEO and Discoverability

- `data/site-config.json` is the single source for the public site name, production base URL, locale, contact email, author identity, series identity, and Twitter card defaults.
- The current production base URL is `https://dark-star-literary-agency.netlify.app`.
- `scripts/update_seo.py --write` generates or refreshes absolute canonical URLs, `og:url`, `og:site_name`, `og:locale`, Twitter card metadata, image-based Open Graph tags where a real local image exists, `robots.txt`, and `sitemap.xml`.
- `scripts/update_structured_data.py --write` generates conservative JSON-LD for the homepage organization, author, and website identities plus the ten canonical Original Adventure storybooks.
- Book JSON-LD intentionally omits prices, offers, stock, format availability, and unverified Amazon claims.
- Redirect pages point their canonical URL at the destination and are excluded from the sitemap.
- Both generator scripts support `--check` and fail when generated output drifts from the configuration or marketplace registry.
- To adopt a future custom domain, change `site_url` once in `data/site-config.json`, run both writers, review the generated diff, and commit the result.

## Deployment

`netlify.toml` defines:

- The static publish directory
- All three build-time content validators
- The generated SEO, sitemap, and structured-data consistency checks
- The permanent legacy Lulu & Ellie redirect
- Baseline security headers
- Conservative cache headers for media, CSS, and JavaScript

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
- Avoid simultaneous autoplay; `media.js` manages viewport-aware playback on connected pages.
- Use `l_e_storage` as the archive/source layer rather than duplicating its full media set into the website repository.

## Contact

Public contact email:

`darstarliteraryagency@gmail.com`
