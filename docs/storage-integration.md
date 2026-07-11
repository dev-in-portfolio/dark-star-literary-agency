# Lulu & Ellie Storage Integration

## Storage repository

The media source repository is:

- `dev-in-portfolio/l_e_storage`
- Default branch: `l_e_storage`

It is the organized source for Original Adventure and shared Lulu & Ellie media.

## Original Adventure structure

The storage repository contains:

- `LULU & ELLIE STORAGE HUB/Original Adventure/Book_1/` through `Book_20/`
- One front cover per book
- One fun/interior feature page per book
- One MP4 book clip per book
- Organization manifests and contact sheets

Useful organization files include:

- `Original Adventure/Organization/book_asset_map.csv`
- `Original Adventure/Organization/front_covers_manifest.json`
- `Original Adventure/Organization/fun_pages_manifest.csv`
- `Original Adventure/Organization/fun_pages_contact_sheet.jpg`
- `General/Organization/general_asset_map.csv`

## Canonical mapping

The public website uses lowercase, web-friendly media folders:

- Storage `Book_1` maps to website `assets/lulu-ellie/original-adventure/book-1`
- Storage `Book_2` maps to website `assets/lulu-ellie/original-adventure/book-2`
- Continue the same number-to-number mapping through Book 20

Do not reorder media folders based on publication date, upload order, Amazon listing order, or file creation time.

## Canonical story order for Books 1-10

1. The Secret of Blackwater Bay
2. The Lost Valley of Thunder
3. The Clockwork Forest
4. The Moonlit Circus
5. The Snow Dragon's Bell
6. The Mushroom Moon Maze
7. The Lanterns of the Deep
8. The Book That Lost Its Ending
9. The Island That Drifted Away
10. The Star Map of Everywhere

The site validator enforces the book-number label, media-folder number, and Previous/Next navigation for this sequence.

## Media policy

- `l_e_storage` is the source/archive layer.
- The public website should contain only optimized public derivatives needed by its pages.
- Do not copy production masters, full print interiors, or duplicate source archives into the website repository.
- Every public MP4 must have a poster image.
- Use `media.js` and `accessibility.css` on media-rich pages.
- New collection media should receive its own manifest before being connected to public pages.

## Local source paths

The storage manifests preserve source paths from the creator's Android Downloads folder. Those paths are provenance references, not portable website paths. They must never be embedded into public HTML.
