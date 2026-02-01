# 80/20 Quran Vocabulary App

A purely client-side web application that visualizes high-frequency vocabulary from the Quran.

## Features

1.  **High Frequency Deck**: Displays the top 50 most frequent words in the entire Quran (excluding common particles).
2.  **Surah Specific Prep**: Allows you to select a specific Surah and view the top 20 most frequent words within that Surah.

## How to Run Locally

Because this application uses the `fetch` API to load the `quran_word_translation.tsv` file, you cannot simply open `index.html` in your browser due to CORS (Cross-Origin Resource Sharing) policies. You must serve the files using a local web server.

### Option 1: Using Python (Recommended)

If you have Python 3 installed (which is common on most systems), you can run:

```bash
# Navigate to the project directory
cd /path/to/repo

# Start a simple HTTP server on port 8000
python3 -m http.server
```

Then, open your browser and navigate to: [http://localhost:8000](http://localhost:8000)

### Option 2: Using Node.js

If you have Node.js installed, you can use `http-server`:

```bash
npx http-server .
```

Then visit the URL shown in the terminal.

### Option 3: VS Code Live Server

If you use Visual Studio Code:
1.  Install the "Live Server" extension.
2.  Right-click on `index.html`.
3.  Select "Open with Live Server".
