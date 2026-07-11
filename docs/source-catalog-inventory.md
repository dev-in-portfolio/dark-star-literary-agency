# Lulu & Ellie Source Catalog Inventory

This document records the source packages used to build the public Companion Library preview.

## Public catalog result

- 44 source PDF interiors
- 12 public collection groups
- Page lengths ranging from 30 to 150 pages
- Approximately 2.02 GB of source material
- All marketplace availability remains unverified unless a separate official listing is manually confirmed

The raw PDF interiors are source and production assets. They are intentionally not copied into this public website repository because the supplied packages expand to more than 2 GB and the website repository already contains a substantial media library.

A source PDF existing does not automatically mean that the title is publication-ready. The manifest records a separate quality status for every interior.

## Supplied source packages

| Source package | PDF interiors represented |
|---|---:|
| Adventure Logs.zip | 5 |
| Branches (1).zip | 5 |
| Branches (2).zip | 6 |
| Branches (3).zip | 6 |
| Branches (4).zip | 7 |
| Branches.zip | 5 |
| Coloring Books.zip | 5 |
| Diary.zip | 5 |

The packages represent 44 distinct PDF interiors after public grouping.

## Public collection groups

1. Adventure Logs — 5 titles
2. Write & Wag — 3 titles
3. Cursive Club — 2 titles
4. Phonics Path — 2 titles
5. Learning Club — 3 titles
6. Field Guides — 4 titles
7. Keepsakes and Diaries — 7 titles
8. Search & Find — 3 titles
9. Puzzle Quest — 5 titles
10. Coloring Collections — 5 titles
11. Kitchen Adventures — 2 titles
12. Bedtime Adventures — 3 titles

## Source manifest

`data/companion-source-manifest.csv` is the traceability record for the supplied PDFs. Each row contains:

- Stable catalog ID
- Public collection and title
- Source ZIP package
- Exact internal PDF path
- Page count
- SHA-256 checksum
- Quality-review status
- Marketplace-verification status
- Last review date

This lets future audits prove which source PDF supports each public catalog entry instead of relying only on matching collection totals.

## Quality statuses

- `polished-preview` — strong preview; final editorial, accessibility, and production QA is still required
- `final-qa-pending` — developed interior awaiting a full final QA pass
- `revision-pass-pending` — developed interior requiring a focused layout and/or character revision pass
- `character-continuity-review` — developed interior requiring a Lulu and Ellie character-continuity review

These labels are internal catalog controls. They do not claim that a title is published or available for purchase.

## Public catalog files

The public catalog uses:

- `data/companion-catalog.json` — structured public catalog
- `companion-library.html` — complete static, indexable presentation of all 44 titles
- `companion-library.js` — runtime consistency check; it does not render or replace the static catalog

`validate_source_manifest.py` reconciles the structured catalog, static `data-source-id` entries, and the checksum-backed source manifest before deployment.

When a title becomes publicly available, update its official book or collection page with a browser-verified purchase link and a verification date. Do not convert the entire Companion Library preview into a purchase-ready catalog based only on the existence of an interior PDF.
