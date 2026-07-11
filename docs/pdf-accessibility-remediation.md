# PDF Accessibility Remediation Standard

## Current baseline

The supplied companion interiors are image-based source PDFs. During the July 11, 2026 source inventory, automated text-extraction inspection found no usable extractable text across the 44 audited interiors. A visually complete source PDF is therefore **not** treated as an accessible digital edition.

The authoritative record is `data/pdf-accessibility-audit.json`. It is keyed to the exact source PDF SHA-256 values in `data/companion-source-manifest.csv`.

Until a record is explicitly approved, its release state remains:

`blocked-for-accessible-digital-distribution`

This does not prevent print production. It prevents the source file from being described or linked as a screen-reader-ready, searchable, accessible digital edition.

## Required remediation sequence

### 1. Preserve the source

- Keep the original source PDF unchanged.
- Record the source SHA-256, page count, package name, and internal filename.
- Create a separate remediation working file and a separately versioned release candidate.

### 2. Create a text foundation

- Add a text layer from the authoritative manuscript or layout source whenever available.
- OCR may be used only as a draft aid when no authoritative text source exists.
- Correct OCR manually page by page, including punctuation, capitalization, contractions, page labels, instructions, answer choices, and repeated activity text.
- Confirm that text selection follows the intended visual order.

### 3. Build semantic structure

- Tag the document as a PDF with a logical structure tree.
- Set one primary document title and language.
- Tag headings in hierarchy order without skipping levels.
- Tag paragraphs, lists, tables, figures, captions, links, and form controls appropriately.
- Mark purely decorative elements as artifacts.
- Do not represent a visual layout table as a data table.

### 4. Establish reading order

- Review every page’s content order manually.
- Ensure instructions are read before the activity they govern.
- Keep labels adjacent to their fields, answer areas, or illustrations.
- Exclude decorative borders, repeated backgrounds, and noninformative page furniture from the reading sequence.
- Confirm that headers, footers, and page numbers do not interrupt the main text.

### 5. Add meaningful alternatives

- Provide concise alt text for informative illustrations.
- Use longer descriptions when an image contains essential story, instructional, diagrammatic, puzzle, or answer information.
- Mark decorative images as artifacts rather than giving them redundant descriptions.
- Do not use filenames, generic phrases such as “image,” or visual-only color references as alternatives.

### 6. Remediate interactive content

- Give every fillable field a programmatic label, role, value, and keyboard order.
- Ensure checkboxes, radio groups, text fields, and buttons have unique accessible names.
- Provide a noninteractive accessible alternative when an activity cannot be meaningfully completed in the PDF format.
- Record when form controls are not applicable to a print-only interior.

### 7. Confirm visual accessibility

- Check text and essential graphic contrast.
- Do not communicate required information through color alone.
- Preserve legible type at practical zoom levels.
- Check that reflow or high-zoom use does not hide instructions or answers.
- Supply text equivalents for handwriting models, tracing exercises, visual puzzles, mazes, and search-and-find activities where needed.

### 8. Validate metadata and navigation

- Set document title, author, subject, language, and descriptive metadata.
- Use the document title rather than the filename in the viewer title bar.
- Add bookmarks for meaningful sections in longer interiors.
- Verify page labels and internal links.

### 9. Manual assistive-technology QA

Automated checks are necessary but not sufficient. Each release candidate requires manual review with at least:

- A keyboard-only pass
- A screen-reader pass in a mainstream desktop environment
- A second-platform spot check where practical
- Text selection and search verification
- Reading-order review at the first, middle, and final pages plus every unique layout type
- Form-control testing for interactive editions

Record the tool versions, reviewer, review date, defects found, and corrections made.

### 10. Approval and release

A record may change to `accessible-digital-release-approved` only when all of these fields are verified:

- `text_layer`: `present-and-manually-verified`
- `tagged_pdf`: `verified`
- `reading_order`: `verified`
- `meaningful_alt_text`: `verified`
- `language_metadata`: `verified`
- `remediation_status`: `approved`

The approved file must receive its own SHA-256 and version identifier. Approval applies only to that exact remediated file—not to later exports or the original source PDF.

## Public-site policy

- Do not link directly to a source PDF from public HTML while its record is blocked.
- Do not use “accessible PDF,” “screen-reader ready,” “searchable edition,” or similar language without an approved registry record.
- A print listing may still exist while the digital accessibility release remains blocked.
- Where an activity cannot be made equivalent in PDF, provide an accessible HTML, EPUB, tagged document, or structured text alternative.

## Priority order

Remediation should start with titles closest to public digital distribution, not simply the most visually polished files. Within an equal release priority, use this order:

1. Bedtime stories and narrative interiors
2. Cookbooks and diaries
3. Handwriting, cursive, phonics, and learning books
4. Adventure logs, keepsakes, and field guides
5. Search-and-find, puzzles, mazes, and coloring activities requiring substantial nonvisual alternatives

## Repository enforcement

`scripts/validate_pdf_accessibility.py` confirms that:

- All 44 source IDs are represented exactly once.
- Source filenames, page counts, and SHA-256 values match the companion manifest.
- Accessibility and remediation states use approved values.
- A file cannot be marked release-approved without all required verification fields.
- Public HTML does not expose unapproved PDF links.
