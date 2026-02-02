# Quran Word-by-Word Dataset Analysis

## Overview
This document provides a technical analysis of the `quran_word_translation.tsv` file. This dataset contains a word-by-word breakdown of the Quran, including Arabic text along with English and Bengali translations, indexed by Surah, Ayah, and Page.

## File Information
- **Filename**: `quran_word_translation.tsv`
- **Format**: Tab-Separated Values (TSV)
- **Encoding**: UTF-8
- **Total Rows**: 77,429
- **Missing Values**: None (0 nulls across all columns)

## Schema / Column Definitions

| Column | Type    | Description                                      | Example Value     |
| :----- | :------ | :----------------------------------------------- | :---------------- |
| `page` | Integer | The page number in the standard Mushaf (1-604).  | `1`               |
| `ayah` | Integer | The verse number within the Surah.               | `1`               |
| `ar`   | String  | The word in Arabic script.                       | `بِسۡمِ`          |
| `en`   | String  | English translation of the word.                 | `In (the) name`   |
| `bn`   | String  | Bengali translation of the word.                 | `নামে`            |
| `surah`| Integer | The chapter (Surah) number (1-114).              | `1`               |
| `root` | String  | The Arabic root of the word.                     | `سمو`             |

## Data Statistics

### Ranges
- **Surah**: 1 to 114
- **Page**: 1 to 604
- **Ayah**: 1 to 286 (Varies per Surah)

### Integrity
- The dataset is complete with no missing values in any of the 6 columns.
- `page`, `ayah`, and `surah` contain valid integer values within expected ranges.
- `root` column contains the triliteral (or otherwise) root of the word, derived from the Quranic Corpus.

## Parsing Instructions

Below is a pseudocode example demonstrating how to parse this TSV file. This approach is language-agnostic and can be adapted to Python, JavaScript, Go, etc.

### Pseudocode

```text
FUNCTION parse_quran_dataset(filepath):
    OPEN file at filepath using UTF-8 encoding

    // Read the first line to get headers
    headers = READ_LINE(file) SPLIT by TAB

    INITIALIZE list quran_data

    FOR EACH line IN file:
        // Split the line by tab character
        columns = SPLIT line by TAB

        // Map columns to variables based on schema
        // Note: Convert numeric columns to Integers
        record = {
            "page":  CONVERT_TO_INT(columns[0]),
            "ayah":  CONVERT_TO_INT(columns[1]),
            "ar":    columns[2],
            "en":    columns[3],
            "bn":    columns[4],
            "surah": CONVERT_TO_INT(columns[5]),
            "root":  columns[6]
        }

        ADD record TO quran_data

    RETURN quran_data
END FUNCTION

// Usage
data = parse_quran_dataset("quran_word_translation.tsv")
PRINT "Total words loaded: " + LENGTH(data)
```

## Usage Notes
- **Encoding**: Ensure the file reader uses `UTF-8` to correctly render Arabic and Bengali characters.
- **Delimiter**: The file uses a tab (`\t`) delimiter, not a comma.
- **Headers**: The first row contains the header names.
