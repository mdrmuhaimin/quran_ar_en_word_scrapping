// Surah Names List (1-114)
const SURAH_NAMES = [
    "Al-Fatihah", "Al-Baqarah", "Al-Imran", "An-Nisa", "Al-Ma'idah", "Al-An'am", "Al-A'raf", "Al-Anfal", "At-Tawbah", "Yunus",
    "Hud", "Yusuf", "Ar-Ra'd", "Ibrahim", "Al-Hijr", "An-Nahl", "Al-Isra", "Al-Kahf", "Maryam", "Ta-Ha",
    "Al-Anbiya", "Al-Hajj", "Al-Mu'minun", "An-Nur", "Al-Furqan", "Ash-Shu'ara", "An-Naml", "Al-Qasas", "Al-Ankabut", "Ar-Rum",
    "Luqman", "As-Sajdah", "Al-Ahzab", "Saba", "Fatir", "Ya-Sin", "As-Saffat", "Sad", "Az-Zumar", "Ghafir",
    "Fussilat", "Ash-Shura", "Az-Zukhruf", "Ad-Dukhan", "Al-Jathiyah", "Al-Ahqaf", "Muhammad", "Al-Fath", "Al-Hujurat", "Qaf",
    "Ad-Dhariyat", "At-Tur", "An-Najm", "Al-Qamar", "Ar-Rahman", "Al-Waqi'ah", "Al-Hadid", "Al-Mujadila", "Al-Hashr", "Al-Mumtahanah",
    "As-Saff", "Al-Jumu'ah", "Al-Munafiqun", "At-Taghabun", "At-Talaq", "At-Tahrim", "Al-Mulk", "Al-Qalam", "Al-Haqqah", "Al-Ma'arij",
    "Nuh", "Al-Jinn", "Al-Muzzammil", "Al-Muddaththir", "Al-Qiyamah", "Al-Insan", "Al-Mursalat", "An-Naba", "An-Nazi'at", "Abasa",
    "At-Takwir", "Al-Infitar", "Al-Mutaffifin", "Al-Inshiqaq", "Al-Buruj", "At-Tariq", "Al-A'la", "Al-Ghashiyah", "Al-Fajr", "Al-Balad",
    "Ash-Shams", "Al-Layl", "Ad-Duhaa", "Ash-Sharh", "At-Tin", "Al-Alaq", "Al-Qadr", "Al-Bayyinah", "Az-Zalzalah", "Al-Adiyat",
    "Al-Qari'ah", "At-Takathur", "Al-Asr", "Al-Humazah", "Al-Fil", "Quraysh", "Al-Ma'un", "Al-Kawthar", "Al-Kafirun", "An-Nasr",
    "Al-Masad", "Al-Ikhlas", "Al-Falaq", "An-Nas"
];

// Common particles to exclude from "High Frequency" deck
const STOP_WORDS = [
    "فِي", "ٱلَّذِينَ", "مِن", "مَا", "لَا", "وَلَا", "إِنَّ", "إِلَّا", "وَمَا", "أَن", "مِنَ", "عَلَىٰ", "ثُمَّ", "مِّن", "مِّنَ", "يَٰٓأَيُّهَا", "إِذَا"
];

const DATA_FILE = 'quran_word_translation.tsv';

let allRows = [];
let globalWordCounts = {}; // word -> count
let globalWordMeanings = {}; // word -> english meaning (taking the most frequent one or first one)
let surahData = {}; // surahId -> Array of rows

document.addEventListener('DOMContentLoaded', () => {
    fetchData();
    initSurahSelector();
});

function fetchData() {
    Papa.parse(DATA_FILE, {
        download: true,
        header: true,
        delimiter: "\t",
        skipEmptyLines: true,
        complete: function(results) {
            console.log("Parsing complete:", results.data.length, "rows.");
            processData(results.data);
            document.getElementById('loading').style.display = 'none';
        },
        error: function(err) {
            console.error("Error parsing TSV:", err);
            document.getElementById('loading').textContent = "Error loading data.";
        }
    });
}

function processData(data) {
    allRows = data;
    globalWordCounts = {};
    surahData = {};

    data.forEach(row => {
        const word = row.ar;
        const meaning = row.en;
        const surahId = parseInt(row.surah);

        if (!word) return;

        // Global counts
        if (!globalWordCounts[word]) {
            globalWordCounts[word] = 0;
            globalWordMeanings[word] = meaning; // Store first meaning found
        }
        globalWordCounts[word]++;

        // Surah data organization
        if (!surahData[surahId]) {
            surahData[surahId] = [];
        }
        surahData[surahId].push(row);
    });

    renderGlobalTop50();
}

function renderGlobalTop50() {
    const container = document.getElementById('global-deck');
    container.innerHTML = '';

    // Convert to array and sort
    const sortedWords = Object.keys(globalWordCounts)
        .map(word => ({
            ar: word,
            count: globalWordCounts[word],
            en: globalWordMeanings[word]
        }))
        .sort((a, b) => b.count - a.count);

    // Filter stop words
    const filteredWords = sortedWords.filter(item => !STOP_WORDS.includes(item.ar));

    // Take top 50
    const top50 = filteredWords.slice(0, 50);

    top50.forEach((item, index) => {
        const card = createCard(item, index + 1);
        container.appendChild(card);
    });
}

function initSurahSelector() {
    const select = document.getElementById('surah-select');

    SURAH_NAMES.forEach((name, index) => {
        const option = document.createElement('option');
        option.value = index + 1; // Surah IDs are 1-based
        option.textContent = `Surah ${index + 1} (${name})`;
        select.appendChild(option);
    });

    select.addEventListener('change', (e) => {
        const surahId = parseInt(e.target.value);
        renderSurahTop20(surahId);
    });
}

function renderSurahTop20(surahId) {
    const container = document.getElementById('surah-deck');
    container.innerHTML = '';

    if (!surahData[surahId]) {
        container.innerHTML = '<p>No data found for this Surah.</p>';
        return;
    }

    const rows = surahData[surahId];
    const localCounts = {};
    const localMeanings = {};

    rows.forEach(row => {
        const word = row.ar;
        if (!localCounts[word]) {
            localCounts[word] = 0;
            localMeanings[word] = row.en;
        }
        localCounts[word]++;
    });

    // Sort by local frequency
    const sortedWords = Object.keys(localCounts)
        .map(word => ({
            ar: word,
            count: localCounts[word],
            en: localMeanings[word]
        }))
        .sort((a, b) => b.count - a.count);

    // Filter stop words? The prompt says "Top 20 most frequent words specifically found in that Surah".
    // Usually, we keep filtering stop words to show meaningful vocab.
    const filteredWords = sortedWords.filter(item => !STOP_WORDS.includes(item.ar));

    const top20 = filteredWords.slice(0, 20);

    top20.forEach((item, index) => {
        const card = createCard(item, index + 1);
        container.appendChild(card);
    });
}

function createCard(item, rank) {
    const card = document.createElement('div');
    card.className = 'card';

    card.innerHTML = `
        <span class="badge">#${rank}</span>
        <div class="card-content">
            <div class="card-front">
                <div class="arabic-word">${item.ar}</div>
                <div style="font-size: 0.8rem; color: #999;">(Click to reveal)</div>
            </div>
            <div class="card-back">
                <div class="english-meaning">${item.en}</div>
                <div class="frequency-count">Occurrences: ${item.count}</div>
            </div>
        </div>
    `;

    card.addEventListener('click', () => {
        card.classList.toggle('revealed');
    });

    return card;
}
