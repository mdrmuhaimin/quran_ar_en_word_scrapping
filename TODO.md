# Future Tasks

The `quran_word_translation.tsv` file has been updated to include a `root` column. The following tasks are pending to fully integrate this change into the application.

## 1. Update Database Schema (`db.js`)
- Modify `createSchema` to include a `root` column in the `words` table.
  ```sql
  CREATE TABLE IF NOT EXISTS words (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      arabic TEXT,
      english TEXT,
      frequency INTEGER,
      root TEXT, -- New column
      surah_counts TEXT
  );
  ```
- Update `processAndInsertData` to parse the `root` field from the TSV and insert it into the database.
  - The TSV parser logic needs to map the new column index or header name.

## 2. Update Data Queries (`db.js`)
- Ensure that queries fetching words (`getDailyWords`, `getTopWords`, `getWordsBySurah`) select the `root` column.
  - Example: `SELECT w.* ...` should already cover it if schema is updated, but verify mapping.

## 3. Update Frontend (`app.js`)
- Update `createStaticCard` and `showCard` to display the root word.
  - Add a DOM element to the card back (e.g., `<div class="word-root">Root: ...</div>`).
- Update `style.css` to style the root word display (e.g., smaller font, lighter color).

## 4. Testing
- Verify that the database rebuilds correctly (IndexedDB might need to be cleared or version bumped).
- Verify that root words appear correctly on flashcards.
- Verify that the application works offline with the new data structure.
