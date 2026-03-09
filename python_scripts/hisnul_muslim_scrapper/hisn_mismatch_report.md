# Hisn Mismatch Audit Report

Generated on 2026-03-08 after regenerating the live merge from:

- Sunnah: https://sunnah.com/hisn
- HadithBD: https://hadithbd.com/books/fullbook/?book=4

Spot-checked online examples:

- Istikharah: https://sunnah.com/hisn:74
- Before sleeping: https://sunnah.com/hisn:99
- Settling a debt: https://sunnah.com/hisn:136
- Comprehensive types of good and manners: https://sunnah.com/hisn:267

## 1. Refreshed dataset summary

The live-regenerated merged file is `hisn_merged.json` with 267 rows.

Arabic comparison status after refresh:

- `exact_match`: 129
- `near_exact`: 14
- `close_match`: 14
- `mismatch`: 61
- `one_missing`: 48
- `both_missing`: 1

Rows with `arabic_match_score != 1.0`: 138

Important note: the previous merged JSON was stale and vastly overstated the problem because HadithBD pagination had not been fetched correctly. This report is based on the refreshed live merge.

## 2. Main conclusion

Most non-`1.0` rows are not bad translations.

They fall into four distinct buckets:

1. Benign orthography/editorial differences
2. Source coverage asymmetry (one source has no Arabic for that row)
3. Same hadith, different granularity (Sunnah keeps narration/instruction; HadithBD keeps only the recited formula or quoted Arabic)
4. Remaining scraper/data problems

## 3. Bucket A: Benign text differences

IDs:

- `near_exact`: 13, 19, 36, 52, 56, 62, 85, 107, 109, 121, 127, 131, 208, 213
- `close_match`: 31, 66, 67, 69, 82, 83, 86, 95, 101, 130, 145, 160, 162, 235

Reason these are not `1.0`:

- orthography differences
- punctuation or quoting differences
- optional bracketed additions in one source
- Qur'anic orthography differences
- minor wording normalization differences

Translation verdict:

- Bengali translation appears materially correct for this whole bucket.
- These rows do not require translation correction.

## 4. Bucket B: Source coverage asymmetry

### 4.1 HadithBD Arabic missing

IDs:

24, 26, 110, 114, 115, 133, 137, 140, 141, 142, 143, 149, 185, 190, 199, 203, 206, 214, 219, 220, 221, 222, 223, 224, 225, 226, 228, 229, 234, 238, 239, 242, 248, 249, 251, 252, 253, 257, 258, 266

Reason:

- The Sunnah row contains Arabic, but the HadithBD row has only Bengali narration/instruction/reference text or no Arabic was captured for that item.

Translation verdict:

- Where Bengali is present, it generally aligns with the English meaning.
- Bengali is missing for IDs `114`, `115`, and `203`.

### 4.2 Sunnah Arabic missing

IDs:

20, 25, 32, 90, 116, 156, 232, 246

Reason:

- Sunnah stores these rows as instruction/context entries without Arabic in the merged field, while HadithBD does provide Arabic.

Translation verdict:

- Bengali translation appears aligned with the English meaning.
- These are comparison asymmetries, not translation failures.

### 4.3 Both Arabic fields missing

ID:

- `244`

Reason:

- Both sources present only instructional prose for the evil-eye note; neither side has Arabic in the merged fields.

Translation verdict:

- Bengali and English are semantically aligned.
- No Arabic comparison is possible.

## 5. Bucket C: Same hadith, different granularity

This is the largest real bucket among `mismatch` rows.

Typical pattern:

- Sunnah keeps the full narration or instructional framing plus the actual recited words.
- HadithBD keeps only the recited formula, only the Qur'anic text, or only the quoted Arabic part.
- SequenceMatcher then gives a low score even though the underlying dua is the same.

Representative IDs:

4, 18, 22, 33, 41, 72, 73, 74, 76, 78, 80, 87, 89, 91, 92, 93, 94, 96, 97, 99, 100, 119, 134, 135, 138, 146, 148, 151, 153, 165, 178, 179, 188, 191, 195, 207, 217, 218, 227, 230, 231, 236, 237, 243, 250, 254, 255, 256, 259, 260, 261, 262, 263, 264, 265

### 5.1 Translation assessment for this bucket

Sub-pattern A: translation materially correct, but HadithBD is storing only the recited formula while Sunnah stores the full narration.

Examples:

- `74` Istikharah
- `151` death agony wording
- `195` sitting/gathering repentance dua
- `227` reply to a disbeliever's greeting
- `254` `SubhanAllahi wa bihamdihi`
- `256` two beloved phrases
- `260` treasure from the treasures of Paradise
- `263` new Muslim taught to say

Verdict:

- The Bengali generally reflects the same hadith context and is not a wrong translation.
- But at the row level it is often not a full sentence-for-sentence equivalent of the Sunnah English row.

Sub-pattern B: translation is context-only or incomplete at the row level.

Examples:

- `18` Bengali only says "say:"
- `20` Bengali gives the instruction but not the full Arabic wording
- `25` Bengali says "then say:"
- `70`, `75`, `99` Bengali gives only the instruction to read the surahs
- `134`, `138` Bengali only says "say:"
- `178`, `179`, `188`, `191`, `217`, `218`, `230`, `231`, `236`, `237`, `243`, `250`, `255`, `259`, `261`, `262`, `264`, `265`

Verdict:

- These are not outright false translations.
- But they are incomplete as full row translations and should not be treated as complete Bengali equivalents of the Sunnah English row.

## 6. Bucket D: Remaining scraper/data defects

These are the rows that still need actual correction.

### 6.1 ID 98

- Chapter: In the morning and evening
- Problem: `arabic_hadithbd` is polluted; it contains the current salawat text and then continues into later evening adhkar.
- Evidence: the HadithBD Arabic field is much longer than the English/Bengali row and clearly contains multiple formulas.
- Translation verdict: the Bengali text (`[সকাল-বিকাল ১০ বার করে]`) is only a repetition note, not a translation of the polluted Arabic field.
- Conclusion: row-level Arabic field is not reliable.

### 6.2 ID 136

- Chapter: Settling a debt
- Problem: `arabic_hadithbd` is the wrong dua. It contains `اللهم إني أعوذ بك من الهم والحزن...` while the English/Bengali row is `اللهم اكفني بحلالك عن حرامك...`.
- Translation verdict: Bengali aligns with Sunnah/English, not with the HadithBD Arabic currently stored in the merged row.
- Conclusion: this is an internal row inconsistency caused by wrong HadithBD Arabic capture or wrong row alignment.

### 6.3 ID 267

- Chapter: Comprehensive types of good and manners
- Problem: `arabic_hadithbd` is footer contamination: `وصلى الله وسلم وبارك على نبينا محمد...`
- Translation verdict: Bengali aligns with the Sunnah row about shutting doors, restraining children at night, and covering vessels.
- Conclusion: HadithBD Arabic is invalid in this row and should be discarded/re-extracted.

## 7. Practical translation verdicts

If you need a concise operational rule for downstream data cleaning:

- Keep as correct: all `near_exact` and `close_match` rows
- Keep as correct-but-granularity-different: most `mismatch` rows where HadithBD stores only the recited formula
- Mark as incomplete translation/context-only: rows such as `18`, `20`, `25`, `70`, `75`, `99`, `134`, `138`, `178`, `179`, `188`, `191`, `217`, `218`, `230`, `231`, `236`, `237`, `243`, `250`, `255`, `259`, `261`, `262`, `264`, `265`
- Mark as translation missing: `114`, `115`, `203`
- Mark as row-corrupt and requiring scraper fix: `98`, `136`, `267`

## 8. Overall judgment

After regenerating from live data, the merged file is much healthier than it first appeared.

The non-`1.0` rows are mostly explained by:

- source asymmetry
- editorial/orthographic differences
- one source storing only the formula while the other stores the full narration

The genuinely problematic rows are a small minority, with the clearest remaining scraper defects at:

- `98`
- `136`
- `267`

If the goal is a production-quality bilingual dataset, these three rows should be fixed first, and the "context-only/incomplete Bengali" rows should then be normalized depending on whether you want:

- the full hadith wording per row, or
- only the recited formula per row.
