# Lulu & Ellie Storage Integration

## Purpose

The public Literary site uses the Lulu & Ellie storage repositories as archive/source layers and `data/library-master.json` as the normalized catalog layer.

The website must never infer publication or marketplace availability merely because a source PDF exists.

## Authoritative Storage Repositories

| Repository | Default branch | Catalog responsibility |
|---|---|---|
| `dev-in-portfolio/l_e_storage` | `l_e_storage` | Original Adventure Books 1–20 and numbered media |
| `dev-in-portfolio/l_e_storage2` | `main` | Lulu & Ellie in Space |
| `dev-in-portfolio/l_e_storage3` | `main` | Creature Rescue Club |
| `dev-in-portfolio/l_e_storage4` | `main` | Mystery Tails + Time Tails |
| `dev-in-portfolio/l_e_storage5` | `main` | Go To Camp |
| `dev-in-portfolio/l_e_storage6` | `main` | Academy / Learning / Phonics / Handwriting / Cursive |
| `dev-in-portfolio/l_e_storage7` | `main` | Companion & Activity Library |

## Normalized Catalog

`data/library-master.json` stores the public site's normalized view of those archives.

Every series record may include:

- source repository;
- expected sequence length where established;
- complete source-book numbers;
- missing source-book numbers;
- public visibility state;
- catalog-reconciliation state;
- source-confirmed public titles where available.

This allows the website to distinguish:

- **source confirmed** from **publicly announced**;
- **publicly announced** from **purchase-ready**;
- **purchase link on file** from **current availability verified**.

## Original Adventure

The Original Adventure archive is fully reconciled.

Source media layout:

- `LULU & ELLIE STORAGE HUB/Original Adventure/Book_1/`
- through `Book_20/`

Each numbered source media folder maps directly to:

- `assets/lulu-ellie/original-adventure/book-1/`
- through `book-20/`

The source media relationship remains strictly number-to-number.

The full source PDFs are archived separately in `l_e_storage/library-import/`. They are not copied into the public website.

## Original Adventure Canonical Titles

1. Lulu & Ellie and the Secret of Blackwater Bay
2. Lulu & Ellie and the Lost Valley of Thunder
3. Lulu & Ellie and the Clockwork Forest
4. Lulu & Ellie and the Moonlit Circus
5. Lulu & Ellie and the Snow Dragon's Bell
6. Lulu & Ellie and the Mushroom Moon Maze
7. Lulu & Ellie and the Lanterns of the Deep
8. Lulu & Ellie and the Book That Lost Its Ending
9. Lulu & Ellie and the Island That Drifted Away
10. Lulu & Ellie and the Star Map of Everywhere
11. Lulu & Ellie and the Lanterns of Firefly Hollow
12. Lulu & Ellie and the Acorn Crown
13. Lulu & Ellie and the Red Kite in the Impossible Wind
14. Lulu & Ellie and the Silver Door Garden
15. Lulu & Ellie and the Moon That Forgot to Laugh
16. Lulu & Ellie and the Emberleaf Kingdom
17. Lulu & Ellie and the Waterfall That Climbed the Stars
18. Lulu & Ellie and the Crystal Pawprint
19. Lulu & Ellie and the Feather of Two Shadows
20. Lulu & Ellie and the Keeper Ring

The public site generator uses this sequence from `library-master.json`; it is no longer duplicated as a hard-coded ten-book validator constant.

## Mystery Tails

The storage archive and earlier public concept pages diverged.

Current source-confirmed public titles for Books 1–5 are:

1. The Case of the Missing Moon Biscuit
2. The Secret of the Whispering Mailbox
3. The Pawprints That Walked Backward
4. The Haunted Treat Truck
5. The Lighthouse That Barked

Earlier concept titles such as *The Case of the Missing Mooncake*, *The Lighthouse That Blinked Twice*, and *The Pawprints in the Pumpkin Patch* are not canonical source-book records.

The public site redirects or noindexes superseded concept pages rather than silently treating them as the archived books.

## Unreconciled Series

In Space, Creature Rescue Club, Go To Camp, Backyard Academy, Bedtime Adventures, and Time Tails have source archive evidence but are not yet treated as fully title-reconciled public catalogs.

Their public series pages show conservative archive status until title-by-title reconciliation is complete.

## Media Policy

Public media should be a web-delivery derivative, not a production master.

The site currently enforces:

- checksum-backed public inventory;
- aggregate/per-file media budgets;
- click-to-load Original Adventure archive video;
- lazy image delivery;
- reduced-motion safeguards;
- number-aligned Original Adventure paths.

Intentional public-media changes require regenerating `data/media-inventory.json` and passing the canonical release gate.

## Source Paths

Storage manifests may preserve original device/download paths for provenance. Those paths are archival metadata only and must never be embedded into public HTML.

## Adding or Updating a Collection

1. Verify the source repository and branch.
2. Confirm source files and sequence.
3. Update `data/library-master.json`.
4. Reconcile public titles only when source evidence supports them.
5. Run `python3 scripts/release_check.py`.
6. Review generated public language and marketplace claims.
7. Merge only after the shared GitHub/Netlify release gate passes.
