# Quran Learning Game (Gamified 80/20 Vocabulary)

A purely client-side, offline-first web application that gamifies the learning of high-frequency Quranic vocabulary.

## Features

### 🎮 Gamified Learning
*   **XP System & Levels**: Earn XP for every word you review. Level up as you master more vocabulary.
*   **Daily Streaks**: Build a habit by completing daily sessions.
*   **Spaced Repetition (SRS)**: The app intelligently schedules words for review based on how well you know them (using a simplified SM-2 algorithm).
*   **Dashboard**: Track your progress, mastery level, and streak.

### 📚 Study Modes
1.  **Daily Session**: A focused session mixing new words with due reviews.
2.  **Browse Words (Global)**: View the top 50 most frequent words in the entire Quran.
3.  **Surah Specific Prep**: Select a Surah (Chapter) to study the top 20 most frequent words found specifically within it.

### 🛠 Technical Architecture
*   **Client-Side Database**: Uses **SQL.js** (SQLite compiled to WebAssembly) to run a relational database entirely in the browser.
*   **Offline Persistence**: Your progress is saved to your browser's **IndexedDB**, allowing you to close the tab and return later without losing data.
*   **No Backend Required**: The app parses the raw `quran_word_translation.tsv` file on the first load to populate its local database.

## How to Run Locally

Because this application uses the `fetch` API and WebAssembly (`wasm`), you must serve the files using a local web server (opening `index.html` directly will not work due to CORS policies).

### Option 1: Using Python (Recommended)

If you have Python 3 installed:

```bash
# Navigate to the project directory
cd /path/to/repo

# Start a simple HTTP server on port 8000
python3 -m http.server
```

Then, open your browser and navigate to: [http://localhost:8000](http://localhost:8000)

### Option 2: Using Node.js

If you have Node.js installed:

```bash
npx http-server .
```

### Option 3: VS Code Live Server

If you use Visual Studio Code:
1.  Install the "Live Server" extension.
2.  Right-click on `index.html`.
3.  Select "Open with Live Server".

## Credits
*   **Data Source**: `quran_word_translation.tsv` (Quranic Corpus).
*   **Font**: [Amiri](https://fonts.google.com/specimen/Amiri) (Google Fonts).
*   **Libraries**:
    *   [PapaParse](https://www.papaparse.com/) (CSV/TSV parsing).
    *   [SQL.js](https://sql.js.org/) (SQLite in the browser).
