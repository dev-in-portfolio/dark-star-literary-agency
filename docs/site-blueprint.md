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
- `/lulu-ellie/original-adventure/` - first collection tier
- `/lulu-and-ellie.html` - legacy redirect only
- `/library.html` - library landing and navigation hub
- `/parents-teachers.html` - parent and teacher trust page
- `/contact.html` - public contact page
- `/series/*.html` - second-level series and collection pages
- `/learning/*.html` - learning line pages
- `/books/*.html` - individual book pages

The homepage introduces the parent agency and routes visitors into the correct area instead of carrying the full Lulu & Ellie experience on one page.

The Lulu & Ellie hub owns the top-level storyworld identity. Collection tiers live below it so each collection can grow without flattening the full catalog into a single page.

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
- Validate links, assets, metadata, and media-folder mappings before deployment.
- Keep book numbers, titles, page slugs, and media directories aligned.
- Use shared CSS and JavaScript instead of introducing new page-specific systems when reusable styling is practical.
- Add absolute canonical, Open Graph, and sitemap URLs only after the production domain is confirmed.

## Public Positioning

The site should feel polished, literary, and magical immediately. Future collections remain hidden unless they are purchase-ready, preorder-ready, sample-ready, or intentionally announced as clearly labeled previews.
