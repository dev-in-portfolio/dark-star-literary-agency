# Dark Star Literary Agency

Static multi-page public website for Dark Star Literary Agency, the creative home of Ambrose Caspian Vale and the Lulu & Ellie Adventures.

## Current Site Structure

- `index.html` - homepage and brand gateway
- `agency.html` - Dark Star Literary Agency identity page
- `ambrose-caspian-vale.html` - author page
- `lulu-ellie/` - current Lulu & Ellie flagship-universe hub
- `lulu-ellie/original-adventure/` - Original Adventure collection tier
- `lulu-and-ellie.html` - legacy redirect to the current Lulu & Ellie hub
- `library.html` - library landing and navigation hub
- `companion-library.html` - source-backed preview of activity, learning, keepsake, puzzle, coloring, cookbook, and bedtime collections
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
- Live books may include official purchase links.
- Intentionally announced previews must use clear `Coming Soon`, `In the Works`, or `Preview` language and must not imply availability.
- Original Adventure Books 1-10 use canonical story order rather than Amazon publication/listing order.

## Companion Catalog

The Companion Library is generated from:

- `data/companion-catalog.json`
- `companion-library.js`
- `companion-library.html`

It currently represents:

- 44 developed interiors
- 12 public collection groups
- Activity logs, handwriting, cursive, phonics, learning, field guides, keepsakes, diaries, search-and-find, puzzles, coloring books, cookbooks, and bedtime stories

The underlying source PDFs remain production assets and are not duplicated into this repository. A completed interior proves that a title is developed; it does not by itself prove that the title is currently available for purchase.

See `docs/source-catalog-inventory.md` for the source-package inventory.

## Media Source Repository

The organized Lulu & Ellie media source is:

- `dev-in-portfolio/l_e_storage`
- Default branch: `l_e_storage`

It contains the Original Adventure Book 1-20 cover, feature/fun-page, and MP4 mappings plus shared General media. The website preserves a strict number-to-number relationship between storage `Book_#` folders and website `book-#` folders.

See `docs/storage-integration.md` for the mapping and media policy.

## Shared Presentation

- `styles.css` contains the main layout, color palette, cards, buttons, badges, book layouts, and responsive behavior.
- `accessibility.css` adds reduced-motion safeguards for media-rich pages.
- `media.js` allows only the most visible motion preview to play and pauses all videos when the page is hidden or reduced motion is requested.

## Validation

Run the repository validator before publishing:

```bash
python scripts/validate_site.py
```

The validator checks:

- Broken local links and missing assets
- Missing page titles, descriptions, and primary headings
- Duplicate element IDs
- Missing image alt text
- Unsafe autoplay video markup
- Original Adventure cover, animation, and feature-page mapping for Books 1-20
- Canonical book numbers, media folders, and Previous/Next navigation for Books 1-10
- Companion catalog structure, 12 collection groups, 44 unique titles, and valid page counts

GitHub Actions runs the same validation on pull requests and pushes to `main` or `agent/**` branches.

## Deployment

`netlify.toml` defines:

- The static publish directory
- Build-time validation
- The permanent legacy Lulu & Ellie redirect
- Baseline security headers
- Conservative cache headers for media, CSS, and JavaScript

The production domain is not hard-coded in the repository. Add absolute canonical, Open Graph, and sitemap URLs after the final public domain is confirmed.

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

1. Live content with verified purchase or download links.
2. Preorder or sample-ready content with working official links.
3. Intentional preview pages that are clearly labeled and make no purchase or release-date claim.

Unapproved drafts, internal production pages, and unfinished downloads stay hidden.

## Purchase Links

- Purchase links are added only when a real official option is ready.
- Preview pages must not use an active-looking purchase control.
- Prefer non-interactive status text over `href="#"` placeholders.
- The current Original Adventure series page retains the official Amazon ASIN links already recorded in the repository.
- Mushroom Moon Maze remains marked temporarily unavailable until a verified listing returns.

## Media Handling

- Keep the media folder number aligned with the canonical public book number.
- Commit optimized public derivatives rather than production masters.
- Use poster images for every animation.
- Avoid simultaneous autoplay; `media.js` manages viewport-aware playback on connected pages.
- Use `l_e_storage` as the archive/source layer rather than duplicating its full media set into the website repository.

## Contact

Public contact email:

`darstarliteraryagency@gmail.com`
