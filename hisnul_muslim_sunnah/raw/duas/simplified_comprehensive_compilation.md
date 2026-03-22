# How `simplified_comprehensive.json` Was Compiled

This note is a reconstruction from the checked-in artifacts in this repo. I did not find a checked-in script or notebook cell that explicitly writes `simplified_comprehensive.json`, so the last step below is inferred from the structure of the JSON files themselves.

## Short Version

The file was almost certainly produced in four stages:

1. Scrape and save raw Sunnah HTML.
2. Split the Sunnah collection page into per-chapter HTML and parse that into Arabic/English chapter data.
3. Merge that Arabic/English data with the Bengali consolidated dataset.
4. Reshape the merged `comprehensive.json` into the cleaner `simplified_comprehensive.json` schema.

## Confirmed Inputs

These files show the compilation chain:

- `hisnul_muslim_sunnah/fetch_sunnah_raw_html.ipynb`
- `hisnul_muslim_sunnah/raw/index.html`
- `hisnul_muslim_sunnah/raw/hadith.html`
- `hisnul_muslim_sunnah/raw/manifest.json`
- `hisnul_muslim_sunnah/raw/duas/html/chapter_001.html` through `chapter_132.html`
- `hisnul_muslim_sunnah/raw/duas/html/manifest.json`
- `hisnul_muslim_sunnah/raw/duas/chapters.json`
- `hisnul_muslim_sunnah/raw/duas/comprehensive.json`
- `hisnul_muslim_bengali_scrapper/md extraction/consolidated.json`
- `hisnul_muslim_sunnah/raw/duas/simplified_comprehensive.json`

## Reconstructed Compilation Process

### 1. Raw Sunnah HTML was fetched and stored

The notebook `hisnul_muslim_sunnah/fetch_sunnah_raw_html.ipynb` contains the scrape pipeline for `https://sunnah.com/hisn`.

From the notebook structure and the files on disk, the flow was:

- fetch the main Sunnah Hisn page
- fetch the per-dua pages `https://sunnah.com/hisn:{id}` for IDs `1..267`
- store the raw HTML under `hisnul_muslim_sunnah/raw/`
- write a raw manifest

That corresponds to:

- `hisnul_muslim_sunnah/raw/index.html`
- `hisnul_muslim_sunnah/raw/hadith.html`
- `hisnul_muslim_sunnah/raw/manifest.json`

### 2. The raw Sunnah page was split into chapter HTML slices

The notebook then split `raw/hadith.html` into per-chapter HTML fragments and saved them under:

- `hisnul_muslim_sunnah/raw/duas/html/chapter_001.html`
- ...
- `hisnul_muslim_sunnah/raw/duas/html/chapter_132.html`

The chapter manifest was saved as:

- `hisnul_muslim_sunnah/raw/duas/html/manifest.json`

This stage produced `132` chapter slices and preserved the chapter-level dua counts.

### 3. The chapter HTML slices were parsed into `chapters.json`

Notebook cell 8 parses those chapter HTML files into:

- `hisnul_muslim_sunnah/raw/duas/chapters.json`

That parser extracts, per chapter:

- `chapter_number`
- `chapter_number_display`
- `arabic_chapter_number_display`
- `english_title`
- `arabic_title`
- `source_file`
- `duas`

And per dua:

- `dua_id`
- `container_id`
- `english_narration`
- `transliteration`
- `translation`
- `english_reference`
- `arabic`

The notebook validates that this stage yields:

- `132` chapters
- `267` duas
- dua IDs `1..267`

### 4. Bengali content was consolidated separately

`comprehensive.json` contains its own source metadata:

- `source_file_arabic_english = "hisnul_muslim_sunnah/raw/duas/chapters.json"`
- `source_file_bengali = "hisnul_muslim_bengali_scrapper/md extraction/consolidated.json"`

So the Bengali side was not pulled directly from Sunnah. It came from:

- `hisnul_muslim_bengali_scrapper/md extraction/consolidated.json`

That Bengali file already contains:

- `chapter_count = 132`
- `dua_count = 267`
- `footnote_count = 300`
- Bengali chapter titles
- Bengali local dua numbering
- Bengali transliteration
- Bengali translation
- Bengali footnotes

### 5. `comprehensive.json` was built by merging the Sunnah parse with the Bengali consolidated file

This step is strongly confirmed by the structure of:

- `hisnul_muslim_sunnah/raw/duas/comprehensive.json`

Its metadata explicitly points to both source files, and its record structure is exactly what you would expect from a merge:

- Arabic/English comes from `chapters.json`
- Bengali data is nested under each dua in a `bengali` object

`comprehensive.json` top-level metadata:

- `source = "sunnah.com/hisn"`
- `source_type = "chapter_html_slices"`
- `source_file_arabic_english = "hisnul_muslim_sunnah/raw/duas/chapters.json"`
- `source_file_bengali = "hisnul_muslim_bengali_scrapper/md extraction/consolidated.json"`
- `bengali_title = "দো'আ ও যিকিরসমূহ"`
- `chapter_count = 132`
- `dua_count = 267`
- `footnote_count = 300`

Per chapter, `comprehensive.json` stores:

- `chapter_number`
- `chapter_number_display`
- `arabic_chapter_number_display`
- `english_title`
- `arabic_title`
- `bengali_id`
- `bengali_title`
- `source_file`
- `duas`

Per dua, it stores:

- the Arabic/English fields from the Sunnah parse
- a nested `bengali` object with:
  - `title`
  - `chapter_dua_id`
  - `bengali_chapter_dua_id`
  - `leading_line`
  - `translitaration`
  - `translation`
  - `footnote_ids`
  - `footnotes`

## Final Step: How `simplified_comprehensive.json` Was Derived

This is the part that is reconstructed rather than directly found in a script.

The structure of:

- `hisnul_muslim_sunnah/raw/duas/simplified_comprehensive.json`

matches a straightforward normalization of `comprehensive.json`.

The counts match exactly:

- `comprehensive.json`: `132` chapters, `267` duas
- `simplified_comprehensive.json`: `132` chapters, `267` hadiths

The ordering also matches chapter-by-chapter and dua-by-dua.

## Field Mapping

The most likely transform was:

### Top level

- `chapter_count` kept as `chapter_count`
- `dua_count` renamed to `hadith_count`
- remove source/manifest metadata

### Chapter level

From `comprehensive.json`:

- `chapter_number`
- `english_title`
- `arabic_title`
- `bengali_title`
- `duas`

To `simplified_comprehensive.json`:

- `chapter_number`
- `title = { arabic, english, bengali }`
- `hadiths`

### Dua / hadith level

From a `comprehensive.json` dua:

- `dua_id`
- `english_narration`
- `transliteration`
- `translation`
- `english_reference`
- `arabic`
- `bengali.chapter_dua_id`
- `bengali.leading_line`
- `bengali.translitaration`
- `bengali.translation`
- `bengali.footnotes`

To a `simplified_comprehensive.json` hadith:

- `numbers.global = dua_id`
- `numbers.local = bengali.chapter_dua_id` when present
- `arabic.text = arabic`
- `english.leading_line = english_narration`
- `english.translitaration = transliteration`
- `english.translation = translation`
- `english.footnote = english_reference`
- `bengali.leading_line = bengali.leading_line`
- `bengali.translitaration = bengali.translitaration`
- `bengali.translation = bengali.translation`
- `bengali.footnote = bengali.footnotes`

Notes:

- The spelling `translitaration` is preserved in both merged outputs.
- `numbers.local` is nullable in places where the Bengali source does not provide a chapter-local dua number.
- Bengali footnotes remain structured objects in the simplified output, not flattened strings.

## What Is Confirmed vs Inferred

### Confirmed

- Raw Sunnah HTML was fetched in `fetch_sunnah_raw_html.ipynb`.
- That HTML was split into `132` chapter HTML files.
- Those chapter files were parsed into `hisnul_muslim_sunnah/raw/duas/chapters.json`.
- `hisnul_muslim_sunnah/raw/duas/comprehensive.json` was built from:
  - `hisnul_muslim_sunnah/raw/duas/chapters.json`
  - `hisnul_muslim_bengali_scrapper/md extraction/consolidated.json`

### Inferred

- The exact code that wrote `simplified_comprehensive.json` is not present in the repo.
- The final output was almost certainly produced by a small reshape step over `comprehensive.json`.
- That reshape renamed `duas` to `hadiths`, packed titles into nested objects, packed text fields into `arabic` / `english` / `bengali` groups, and renamed `dua_count` to `hadith_count`.

## Practical Rebuild Recipe

If we needed to rebuild it again, the likely recipe would be:

1. Run the Sunnah notebook to regenerate:
   - raw HTML
   - chapter HTML slices
   - `raw/duas/chapters.json`
2. Regenerate or reuse:
   - `hisnul_muslim_bengali_scrapper/md extraction/consolidated.json`
3. Merge those two sources into:
   - `hisnul_muslim_sunnah/raw/duas/comprehensive.json`
4. Apply a final reshape step to emit:
   - `hisnul_muslim_sunnah/raw/duas/simplified_comprehensive.json`

## Bottom Line

`simplified_comprehensive.json` was not compiled directly from Sunnah HTML. It was almost certainly compiled from the already merged bilingual dataset in `comprehensive.json`, which itself was built by combining:

- the Sunnah-derived Arabic/English parse in `raw/duas/chapters.json`
- the Bengali consolidated dataset in `hisnul_muslim_bengali_scrapper/md extraction/consolidated.json`
