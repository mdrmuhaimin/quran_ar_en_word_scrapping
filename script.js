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

// Bengali Surah Names
const SURAH_NAMES_BN = [
    "আল-ফাতিহা", "আল-বাকারা", "আলে-ইমরান", "আন-নিসা", "আল-মায়িদাহ", "আল-আনআম", "আল-আরাফ", "আল-আনফাল", "আত-তাওবাহ", "ইউনুস",
    "হুদ", "ইউসুফ", "আর-রা'দ", "ইব্রাহীম", "আল-হিজর", "আন-নাহল", "আল-ইসরা", "আল-কাহফ", "মারইয়াম", "ত্ব-হা",
    "আল-আম্বিয়া", "আল-হাজ্জ", "আল-মুমিনুন", "আন-নূর", "আল-ফুরকান", "আশ-শুআরা", "আন-নামল", "আল-কাসাস", "আল-আনকাবুত", "আর-রূম",
    "লোকমান", "আস-সাজদাহ", "আল-আহযাব", "সাবা", "ফাতির", "ইয়াসীন", "আস-সাফফাত", "সাদ", "আয-যুমার", "গাফির",
    "ফুসসিলাত", "আশ-শূরা", "আয-যুখরুফ", "আদ-দুখান", "আল-জাসিয়াহ", "আল-আহকাফ", "মুহাম্মদ", "আল-ফাতহ", "আল-হুজুরাত", "ক্বাফ",
    "আয-যারিয়াত", "আত-তূর", "আন-নাজম", "আল-কামার", "আর-রাহমান", "আল-ওয়াকিয়াহ", "আল-হাদীদ", "আল-মুজাদালাহ", "আল-হাশর", "আল-মুমতাহিনাহ",
    "আস-সাফ", "আল-জুমুআহ", "আল-মুনাফিকুন", "আত-তাগাবুন", "আত-তালাক", "আত-তাহরীম", "আল-মুলক", "আল-কলম", "আল-হাক্কাহ", "আল-মাআরিজ",
    "নূহ", "আল-জিন্ন", "আল-মুজ্জাম্মিল", "আল-মুদ্দাসসির", "আল-কিয়ামাহ", "আল-ইনসান", "আল-মুরসালাত", "আন-নাবা", "আন-নাযিয়াত", "আবাসা",
    "আত-তাকভীর", "আল-ইনফিতার", "আল-মুতাফফিফীন", "আল-ইনশিকাক", "আল-বুরুজ", "আত-তারিক", "আল-আলা", "আল-গাশিয়াহ", "আল-ফজর", "আল-বালাদ",
    "আশ-শামস", "আল-লাইল", "আদ-দুহা", "আশ-শারহ", "আত-তীন", "আল-আলাক", "আল-কদর", "আল-বাইয়িনাহ", "আয-যালযালাহ", "আল-আদিয়াত",
    "আল-কারিয়াহ", "আত-তাকাসুর", "আল-আসর", "আল-হুমাজাহ", "আল-ফীল", "কুরাইশ", "আল-মাউন", "আল-কাউসার", "আল-কাফিরুন", "আন-নাসর",
    "আল-মাসাদ", "আল-ইখলাস", "আল-ফালাক", "আন-নাস"
];

// UI Translations
const UI_TRANSLATIONS = {
    "header_title": {
        "en": "80/20 Quran Vocabulary",
        "bn": "৮০/২০ কুরআন শব্দভাণ্ডার"
    },
    "header_subtitle": {
        "en": "Master the most frequent words of the Quran.",
        "bn": "কুরআনের সবচেয়ে বহুল ব্যবহৃত শব্দগুলি শিখুন।"
    },
    "loading_text": {
        "en": "Loading data...",
        "bn": "ডেটা লোড হচ্ছে..."
    },
    "global_section_title": {
        "en": "High Frequency Deck (Top 50)",
        "bn": "সর্বাধিক ব্যবহৃত শব্দ (শীর্ষ ৫০)"
    },
    "global_section_subtitle": {
        "en": "These words appear most frequently throughout the Quran.",
        "bn": "এই শব্দগুলি কুরআনে সবচেয়ে বেশিবার এসেছে।"
    },
    "surah_section_title": {
        "en": "Surah Specific Prep",
        "bn": "সূরা ভিত্তিক প্রস্তুতি"
    },
    "surah_select_label": {
        "en": "Select a Surah:",
        "bn": "একটি সূরা নির্বাচন করুন:"
    },
    "surah_select_default": {
        "en": "Choose a Surah...",
        "bn": "একটি সূরা চয়ন করুন..."
    },
    "surah_section_subtitle": {
        "en": "Top 20 frequent words in the selected Surah.",
        "bn": "নির্বাচিত সূরার শীর্ষ ২০টি বহুল ব্যবহৃত শব্দ।"
    },
    "card_click_reveal": {
        "en": "(Click to reveal)",
        "bn": "(দেখতে ক্লিক করুন)"
    },
    "card_occurrences": {
        "en": "Occurrences",
        "bn": "ব্যবহার সংখ্যা"
    },
    "no_data_surah": {
        "en": "No data found for this Surah.",
        "bn": "এই সূরার জন্য কোন তথ্য পাওয়া যায়নি."
    }
};

// Common particles to exclude from "High Frequency" deck
const STOP_WORDS = [
    "فِي", "ٱلَّذِينَ", "مِن", "مَا", "لَا", "وَلَا", "إِنَّ", "إِلَّا", "وَمَا", "أَن", "مِنَ", "عَلَىٰ", "ثُمَّ", "مِّن", "مِّنَ", "يَٰٓأَيُّهَا", "إِذَا"
];

const DATA_FILE = 'quran_word_translation.tsv';

let allRows = [];
let globalWordCounts = {}; // word -> count
let globalWordMeanings = {}; // word -> { en: ..., bn: ... }
let surahData = {}; // surahId -> Array of rows
let currentLanguage = localStorage.getItem('language') || 'en';

document.addEventListener('DOMContentLoaded', () => {
    initLanguageSelector();
    applyLanguage(); // Apply language immediately
    fetchData();
    initSurahSelector();
});

function initLanguageSelector() {
    const select = document.getElementById('language-select');
    select.value = currentLanguage;
    select.addEventListener('change', (e) => {
        currentLanguage = e.target.value;
        localStorage.setItem('language', currentLanguage);
        applyLanguage();
    });
}

function applyLanguage() {
    document.documentElement.lang = currentLanguage;

    // Update static text
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (UI_TRANSLATIONS[key] && UI_TRANSLATIONS[key][currentLanguage]) {
            el.textContent = UI_TRANSLATIONS[key][currentLanguage];
        }
    });

    // Re-render components if data is loaded
    if (allRows.length > 0) {
        renderSurahSelector(); // Update surah names
        renderGlobalTop50();

        // If a surah is selected, re-render that too
        const surahSelect = document.getElementById('surah-select');
        if (surahSelect.value) {
            renderSurahTop20(parseInt(surahSelect.value));
        }
    }
}

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
    globalWordMeanings = {};

    data.forEach(row => {
        const word = row.ar;
        const meaningEn = row.en;
        const meaningBn = row.bn;
        const surahId = parseInt(row.surah);

        if (!word) return;

        // Global counts
        if (!globalWordCounts[word]) {
            globalWordCounts[word] = 0;
            globalWordMeanings[word] = { en: meaningEn, bn: meaningBn };
        }
        globalWordCounts[word]++;

        // Surah data organization
        if (!surahData[surahId]) {
            surahData[surahId] = [];
        }
        surahData[surahId].push(row);
    });

    renderSurahSelector();
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
            meaning: globalWordMeanings[word][currentLanguage] || globalWordMeanings[word]['en']
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
    renderSurahSelector();

    select.addEventListener('change', (e) => {
        const surahId = parseInt(e.target.value);
        renderSurahTop20(surahId);
    });
}

function renderSurahSelector() {
    const select = document.getElementById('surah-select');
    const selectedValue = select.value; // Preserve selection

    // Keep the first option (placeholder) or recreate it
    // Better to recreate to ensure text is updated
    select.innerHTML = '';

    const placeholder = document.createElement('option');
    placeholder.value = "";
    placeholder.disabled = true;
    placeholder.selected = true;
    placeholder.textContent = UI_TRANSLATIONS['surah_select_default'][currentLanguage];
    select.appendChild(placeholder);

    const names = currentLanguage === 'bn' ? SURAH_NAMES_BN : SURAH_NAMES;

    names.forEach((name, index) => {
        const option = document.createElement('option');
        option.value = index + 1; // Surah IDs are 1-based
        option.textContent = currentLanguage === 'bn'
            ? `সূরা ${index + 1} (${name})`
            : `Surah ${index + 1} (${name})`;
        select.appendChild(option);
    });

    if (selectedValue) {
        select.value = selectedValue;
    }
}

function renderSurahTop20(surahId) {
    const container = document.getElementById('surah-deck');
    container.innerHTML = '';

    if (!surahData[surahId]) {
        container.innerHTML = `<p>${UI_TRANSLATIONS['no_data_surah'][currentLanguage]}</p>`;
        return;
    }

    const rows = surahData[surahId];
    const localCounts = {};
    const localMeanings = {};

    rows.forEach(row => {
        const word = row.ar;
        if (!localCounts[word]) {
            localCounts[word] = 0;
            localMeanings[word] = currentLanguage === 'bn' ? row.bn : row.en;
        }
        localCounts[word]++;
    });

    // Sort by local frequency
    const sortedWords = Object.keys(localCounts)
        .map(word => ({
            ar: word,
            count: localCounts[word],
            meaning: localMeanings[word]
        }))
        .sort((a, b) => b.count - a.count);

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

    const clickToReveal = UI_TRANSLATIONS['card_click_reveal'][currentLanguage];
    const occurrencesLabel = UI_TRANSLATIONS['card_occurrences'][currentLanguage];

    card.innerHTML = `
        <span class="badge">#${rank}</span>
        <div class="card-content">
            <div class="card-front">
                <div class="arabic-word">${item.ar}</div>
                <div style="font-size: 0.8rem; color: #999;">${clickToReveal}</div>
            </div>
            <div class="card-back">
                <div class="english-meaning">${item.meaning}</div>
                <div class="frequency-count">${occurrencesLabel}: ${item.count}</div>
            </div>
        </div>
    `;

    card.addEventListener('click', () => {
        card.classList.toggle('revealed');
    });

    return card;
}
