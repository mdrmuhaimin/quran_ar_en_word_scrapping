# Dua Dataset Requirements

## Goal

Create a structured, dua-level dataset from the manually reviewed page transcripts in `hisnul_muslim_bengali_scrapper/page_transcripts_manual`.

The dataset must extract one logical dua entry per row and preserve these fields:

- Arabic
- Bengali transliteration
- Bengali translation
- References

## Source Of Truth

- Primary source: `hisnul_muslim_bengali_scrapper/page_transcripts_manual/page_023.txt` through `page_307.txt`
- Supporting visual source for dispute resolution: `hisnul_muslim_bengali_scrapper/rendered_pages/page_XXX.png`
- `page_307.txt` is a blank page marker and must not produce a dua row

## Scope

- Include the dua content section covered by the reviewed transcripts
- Exclude blank pages
- Exclude footer-only citation blocks unless they belong to the current dua's reference text
- Exclude publisher chrome and decorative page elements
- Preserve multi-page duas as single logical entries

## Required Output

Produce a UTF-8 CSV named:

- `hisnul_muslim_bengali_scrapper/bn_hisnul_dua_dataset.csv`

Each row must represent one logical dua or one instruction-style entry that is presented as a numbered item in the source.

## Required Columns

- `dua_seq`
  - Sequential integer based on the Bengali book order
- `section_title_bn`
  - Bengali section title, for example a heading like `৮১. স্ত্রী-সহবাসের পূর্বের দো‘আ`
- `page_start`
  - First PDF page where the dua appears
- `page_end`
  - Last PDF page where the dua appears
- `entry_number_bn`
  - Printed entry number if present, for example `192`, `233-(1)`, or `240-(2)`
- `arabic`
  - Arabic dua text only
- `transliteration_bn`
  - Bengali-script transliteration line(s)
- `translation_bn`
  - Bengali meaning/translation text
- `reference_bn`
  - Bengali reference/citation text tied to the entry
- `notes`
  - Optional parser notes for ambiguous or irregular entries

## Parsing Rules

### Entry Boundaries

- A new row starts when the source introduces a new numbered entry or a new instruction-style numbered item.
- If a dua spans multiple pages, merge it into one row.
- If a section heading appears before the next numbered item, attach that heading to the following row(s) until a new section heading appears.

### Arabic

- Capture only the Arabic dua or Arabic quotation tied to the current entry.
- Do not merge Bengali commentary into `arabic`.
- Preserve Arabic wording exactly as transcribed, including punctuation where present.
- If Arabic is absent in the reviewed transcript for a valid entry, leave `arabic` empty rather than inventing text.

### Transliteration

- Capture Bengali-script transliteration only.
- Exclude surrounding translation or commentary.
- Merge wrapped transliteration lines into one field with normalized spaces.

### Translation

- Capture the Bengali explanatory or quoted meaning for the current entry.
- Preserve the meaning text as printed, including quotation marks if present.
- If the printed translation continues on the next page, merge it into one field.

### References

- Capture only source citations, hadith references, and related citation notes for the current entry.
- Exclude unrelated page footer text that belongs to a previous or next entry.
- If a reference block is shared by multiple subentries on the same page and clearly belongs to all of them, duplicate it into each relevant row.

## Normalization Rules

- Trim leading and trailing whitespace for all fields.
- Convert internal line wraps within the same field to single spaces.
- Preserve Bengali and Arabic characters exactly; do not transliterate between scripts.
- Preserve existing punctuation and parentheses unless they are obvious line-break artifacts.
- Do not renumber entries.

## Multi-Page Handling

- `page_start` must be the first page where the entry begins.
- `page_end` must be the last page where the entry ends.
- A field may begin on one page and end on another; the final row must contain the merged field text.
- If a page contains only the continuation of the previous entry and no new entry start, it must not create a new row.

## Special Cases

- Numbered subentries like `(1)` and `(2)` count as distinct rows only if the source presents them as separate numbered formulas or separate meanings.
- Section-level prose that is not a numbered entry should not become its own row unless it functions as the only visible content of an indexed item.
- Closing material after the dua section, including book-level notes, must not become dataset rows.

## Quality Requirements

- No duplicate rows for the same printed entry
- No missing rows caused by page-split entries
- No page footer bleed into `arabic`, `transliteration_bn`, `translation_bn`, or `reference_bn`
- Every row must have at least one of:
  - `arabic`
  - `translation_bn`
  - `transliteration_bn`
- Every row must have `page_start`, `page_end`, and `section_title_bn`

## Validation Requirements

The dataset build must include checks for:

- duplicate `entry_number_bn` values where duplication is not expected
- rows with all content fields empty
- rows with `page_end < page_start`
- orphan reference rows with no associated entry content
- suspicious rows containing only citation text or only section headers

## Optional Secondary Output

Also produce a review file:

- `hisnul_muslim_bengali_scrapper/bn_hisnul_dua_dataset_review.csv`

Recommended extra review columns:

- `raw_pages`
- `parse_status`
- `review_flag`
- `source_excerpt`

## Acceptance Criteria

- The final dataset is generated from the reviewed transcript files, not from OCR-only text.
- The dataset is one row per logical dua entry.
- Arabic, transliteration, Bengali translation, and references are separated into distinct columns.
- Multi-page entries are merged correctly.
- Closing notes and blank pages do not appear as dua rows.
- The output is consistent enough for downstream alignment against Sunnah or other structured sources.
