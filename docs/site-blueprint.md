# Site Blueprint

Dark Star Literary Agency is a public-facing launch site for three connected brands:

- Dark Star Literary Agency - the professional umbrella
- Ambrose Caspian Vale - the author brand
- Lulu & Ellie Adventures - the flagship children's universe

## Current Page Strategy

The site is a static multi-page public experience:

- `/` - homepage and brand gateway
- `/agency.html` - Dark Star Literary Agency identity page
- `/ambrose-caspian-vale.html` - author page
- `/lulu-ellie/` - current flagship-universe hub
- `/lulu-ellie/original-adventure/` - first media-rich collection tier
- `/lulu-and-ellie.html` - legacy redirect only
- `/library.html` - storybook, series, and learning-line navigation hub
- `/companion-library.html` - structured preview catalog for developed activity and companion interiors
- `/parents-teachers.html` - parent and teacher trust page
- `/contact.html` - public contact page
- `/series/*.html` - second-level series and collection pages
- `/learning/*.html` - learning line pages
- `/books/*.html` - individual book pages

The homepage introduces the parent agency and routes visitors into the correct area instead of carrying the full Lulu & Ellie experience on one page.

The Lulu & Ellie hub owns the top-level storyworld identity. Collection tiers live below it so each collection can grow without flattening the full catalog into a single page.

## Catalog Architecture

### Original Adventure

- Books 1-10 are presented in canonical story order.
- Public purchase links use official ASIN links only where already confirmed.
- Book numbers, individual pages, Previous/Next navigation, and `book-#` media folders must agree.
- The 20-volume media tier can represent later preview volumes without claiming that each has a complete public book page.

### Companion Library

- `data/companion-catalog.json` is the structured source of truth.
- `companion-library.js` renders the catalog into `companion-library.html`.
- The initial catalog contains 44 developed interiors across 12 public collection groups.
- Completed interiors are presented as source-backed previews, not automatic proof of purchase availability.
- Raw interiors and production masters remain outside the website repository.

### Media Archive

- `dev-in-portfolio/l_e_storage` is the organized archive/source repository for Original Adventure and General Lulu & Ellie media.
- Storage `Book_#` folders map directly to website `book-#` folders.
- Publication order, Amazon listing order, file timestamps, and upload order must never change the canonical media mapping.

## Catalog Status Model

Every public catalog item must be one of the following:

- **Live** - available through a verified official purchase or download link
- **Preorder / Sample Ready** - supported by a working official preorder or sample link
- **Intentional Preview** - clearly marked `Coming Soon`, `In the Works`, or `Preview`, with no false purchase or release-date claim
- **Hidden Draft** - internal only and absent from public navigation

## Design Direction

- Midnight navy and black-blue background
- Soft gold accents
- Ivory text
- Subtle star and portal glow
- Premium literary styling with warmer child-friendly accents inside Lulu & Ellie content
- Motion previews that respect reduced-motion preferences and do not all play simultaneously

## Technical Direction

- Keep the public output static and indexable.
- Validate links, assets, metadata, media-folder mappings, canonical book order, and companion-catalog structure before deployment.
- Keep book numbers, titles, page slugs, Previous/Next links, and media directories aligned.
- Use shared CSS and JavaScript instead of introducing new page-specific systems when reusable styling is practical.
- Keep source archives and full production interiors out of the website repository.
- Add absolute canonical, Open Graph, and sitemap URLs only after the production domain is confirmed.

## Public Positioning

The site should feel polished, literary, and magical immediately. Future collections remain hidden unless they are purchase-ready, preorder-ready, sample-ready, or intentionally announced as clearly labeled previews.
