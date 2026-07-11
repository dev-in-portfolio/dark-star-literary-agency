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
- Original Adventure cover, animation, and feature-page mapping

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

## Purchase Placeholders

- Purchase links are added only when real official options are ready.
- Preview pages must not use an active-looking purchase control.
- Prefer non-interactive status text over `href="#"` placeholders.

## Media Handling

- Keep the media folder number aligned with the public book number.
- Commit optimized public derivatives rather than production masters.
- Use poster images for every animation.
- Avoid simultaneous autoplay; `media.js` manages viewport-aware playback on connected pages.

## Contact

Public contact email:

`darstarliteraryagency@gmail.com`
