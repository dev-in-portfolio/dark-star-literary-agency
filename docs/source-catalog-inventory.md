# Lulu & Ellie Source Catalog Inventory

This document records the source packages used to build the public Companion Library preview.

## Public catalog result

- 44 developed interiors
- 12 public collection groups
- Page lengths ranging from 30 to 150 pages
- All titles remain previews unless a separate official purchase listing is confirmed

The raw PDF interiors are source/production assets. They are intentionally not copied into this public website repository because the supplied packages expand to roughly 2 GB and the website repository already contains a substantial media library.

## Supplied source packages

| Source package | Developed interiors represented |
|---|---:|
| Adventure Logs.zip | 5 |
| Branches (1).zip | 5 |
| Branches (2).zip | 6 |
| Branches (3).zip | 6 |
| Branches (4).zip | 7 |
| Branches.zip | 7 |
| Coloring Books.zip | 5 |
| Diary.zip | 5 |

Some packages contain more than one public collection. After deduplication and public grouping, the packages represent 44 distinct interiors.

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

## Structured source of truth

The public catalog is maintained in:

- `data/companion-catalog.json`

The presentation page and renderer are:

- `companion-library.html`
- `companion-library.js`

When a title becomes publicly available, update its official book or collection page with a verified purchase link. Do not convert the entire Companion Library preview into a purchase-ready catalog based only on the existence of an interior PDF.
