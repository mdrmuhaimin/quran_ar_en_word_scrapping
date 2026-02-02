const UI_TRANSLATIONS = {
    en: {
        title: "Quran Learning Game",
        dashboard: "Dashboard",
        browse: "Browse Words",
        initializing: "Initializing Database...",
        level: "Level",
        streak: "Streak",
        mastery: "Mastery",
        days: "Days",
        of_top: "of Top 80%",
        start_session: "Start Daily Session",
        session_info: "Review 10 words to keep your streak!",
        word_progress: "Word",
        quit: "Quit",
        tap_hint: "(Tap to flip)",
        hard: "Hard (+5 XP)",
        good: "Good (+10 XP)",
        easy: "Easy (+15 XP)",
        global_top: "Global Top 50",
        global_desc: "Most frequent words excluding particles.",
        surah_filter: "Surah Filter",
        choose_surah: "Choose a Surah...",
        surah_freq: "Surah Freq",
        global_freq: "Global Freq",
        session_complete: "Session Complete! Great job.",
        no_words: "No words available! Database empty?"
    },
    bn: {
        title: "কুরআন শিক্ষা গেম",
        dashboard: "ড্যাশবোর্ড",
        browse: "শব্দ ব্রাউজ করুন",
        initializing: "ডেটাবেস লোড হচ্ছে...",
        level: "লেভেল",
        streak: "স্ট্রিক",
        mastery: "দক্ষতা",
        days: "দিন",
        of_top: "শীর্ষ ৮০% এর",
        start_session: "দৈনিক সেশন শুরু করুন",
        session_info: "স্ট্রিক ধরে রাখতে ১০টি শব্দ অনুশীলন করুন!",
        word_progress: "শব্দ",
        quit: "প্রস্থান",
        tap_hint: "(উল্টাতে ট্যাপ করুন)",
        hard: "কঠিন (+৫ XP)",
        good: "ভালো (+১০ XP)",
        easy: "সহজ (+১৫ XP)",
        global_top: "গ্লোবাল শীর্ষ ৫০",
        global_desc: "সবচেয়ে বেশি ব্যবহৃত শব্দসমূহ।",
        surah_filter: "সূরা ফিল্টার",
        choose_surah: "একটি সূরা বাছুন...",
        surah_freq: "সূরা ফ্রিকোয়েন্সি",
        global_freq: "গ্লোবাল ফ্রিকোয়েন্সি",
        session_complete: "সেশন সম্পন্ন! দারুণ কাজ।",
        no_words: "কোনো শব্দ পাওয়া যায়নি! ডেটাবেস খালি?"
    }
};

const SURAH_NAMES_BN = [
    "আল-ফাতিহা", "আল-বাকারা", "আলে-ইমরান", "আন-নিসা", "আল-মায়িদাহ", "আল-আনআম", "আল-আরাফ", "আল-আনফাল", "আত-তাওবাহ", "ইউনাস",
    "হুদ", "ইউসুফ", "আর-রাদ", "ইব্রাহীম", "আল-হিজর", "আন-নাহল", "বনী-ইসরাঈল", "আল-কাহফ", "মারইয়াম", "ত্ব-হা",
    "আল-আম্বিয়া", "আল-হজ্জ", "আল-মুমিনুন", "আন-নূর", "আল-ফুরকান", "আশ-শুকারা", "আন-নামল", "আল-কাসাস", "আল-আনকাবুত", "আর-রূম",
    "লোকমান", "আস-সেজদাহ", "আল-আহযাব", "সাবা", "ফাতির", "ইয়াসীন", "আস-সাফফাত", "সাদ", "আয-যুমার", "আল-মুমিন",
    "হা-মীম সেজদাহ", "আশ-শূরা", "আয-যুখরুফ", "আদ-দুখাত", "আল-জাসিয়া", "আল-আহক্বাফ", "মুহাম্মদ", "আল-ফাতহ", "আল-হুজুরাত", "ক্বাফ",
    "আয-যারিয়াত", "আত্ব-তূর", "আন-নাজম", "আল-ক্বামার", "আর-রাহমান", "আল-ওয়াকিয়াহ", "আল-হাদীদ", "আল-মুজাদালাহ", "আল-হাশর", "আল-মুমতাহিনাহ",
    "আস-সাফ", "আল-জুমুআহ", "আল-মুনাফিকুন", "আত-তাগাবুন", "আত-ত্বালাক", "আত-তাহরীম", "আল-মুলক", "আল-কলম", "আল-হাক্কাহ", "আল-মাআরিজ",
    "নূহ", "আল-জ্বিন", "আল-মুজ্জাম্মিল", "আল-মুদ্দাসসির", "আল-কিয়ামাহ", "আল-ইনসান", "আল-মুরসালাত", "আন-নাবা", "আন-নাজিয়াত", "আবাসা",
    "আত-তাকভীর", "আল-ইনফিতার", "আল-মুতাফফিফীন", "আল-ইনশিকাক", "আল-বুরুজ", "আত-তারিক", "আল-আলা", "আল-গাশিয়াহ", "আল-ফজর", "আল-বালাদ",
    "আশ-শামস", "আল-লাইল", "আদ-দোহা", "আল-ইনশিরাহ", "আত-তীন", "আল-আলাক", "আল-কদর", "আল-বাইয়্যিনাহ", "আল-যিলযাল", "আল-আদিয়াত",
    "আল-কারিআহ", "আত-তাকাসুর", "আল-আসর", "আল-হুমাযাহ", "আল-ফীল", "কুরাইশ", "আল-মাউন", "আল-কাউসার", "আল-কাফিরুন", "আন-নাসর",
    "আল-লাহাব", "আল-ইখলাস", "আল-ফালাক", "আন-নাস"
];

const App = {
    // State
    sessionWords: [],
    currentWordIndex: 0,
    currentWord: null,
    isFlipped: false,
    currentLanguage: 'en',

    async init() {
        console.log("App initializing...");
        try {
            await DB.init();

            // Load saved language
            const savedLang = localStorage.getItem('preferredLanguage');
            if (savedLang && UI_TRANSLATIONS[savedLang]) {
                this.currentLanguage = savedLang;
            }

            // Check streak on login
            this.handleLogin();

            this.updateDashboard();
            this.setupEventListeners();

            // Initialize Language and Apply
            this.initLanguageSelector();
            this.applyLanguage(this.currentLanguage);

            // Switch to dashboard
            document.getElementById('loading-screen').classList.add('hidden');
            document.getElementById('dashboard-screen').classList.remove('hidden');

        } catch (e) {
            console.error("Initialization failed:", e);
            document.getElementById('loading-text').textContent = "Error: " + e.message;
        }
    },

    initLanguageSelector() {
        const selector = document.getElementById('language-select');
        if(selector) {
            selector.value = this.currentLanguage;
            selector.addEventListener('change', (e) => {
                this.applyLanguage(e.target.value);
            });
        }
    },

    applyLanguage(lang) {
        this.currentLanguage = lang;
        localStorage.setItem('preferredLanguage', lang);
        const t = UI_TRANSLATIONS[lang];

        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            if(t[key]) {
                if(el.tagName === 'INPUT' && el.type === 'placeholder') {
                    el.placeholder = t[key];
                } else {
                    el.textContent = t[key];
                }
            }
        });

        // Update Surah selector
        this.initSurahSelector();

        // Update active card content if game is active
        if(!document.getElementById('game-screen').classList.contains('hidden')) {
            this.showCard();
        }

        // Update browse screen content if active
        if(!document.getElementById('browse-screen').classList.contains('hidden')) {
            const surahSelect = document.getElementById('surah-select');
            if(surahSelect.value) {
                this.renderSurahDeck(surahSelect.value);
            }
            this.renderGlobalDeck();
        }
    },

    handleLogin() {
        const profile = DB.getProfile();
        const today = new Date().toISOString().split('T')[0];

        const streakAction = GameLogic.checkStreak(profile.last_login_date);
        let newStreak = profile.current_streak;

        if (streakAction === 'increment') newStreak++;
        else if (streakAction === 'reset') newStreak = 1; // Or 0? Let's say 1 for today.

        DB.updateProfile({
            current_streak: newStreak,
            last_login_date: today
        });
    },

    updateDashboard() {
        const profile = DB.getProfile();
        const level = GameLogic.getLevel(profile.total_xp);
        const progress = GameLogic.getLevelProgress(profile.total_xp);

        document.getElementById('user-level').textContent = level;
        document.getElementById('user-xp').textContent = `${profile.total_xp} XP`;
        document.getElementById('xp-bar-fill').style.width = `${progress}%`;
        document.getElementById('user-streak').textContent = profile.current_streak;

        // Mastery calculation: Words with strength > 3 / Total words (approx 80% coverage check would be complex, simplifying)
        // For now just simplified mastery stat
        // We could query DB for count of strength > 3
        const res = DB.db.exec("SELECT COUNT(*) FROM user_progress WHERE strength_level >= 4");
        const masteredCount = res[0].values[0][0];
        const totalWords = 77430; // Approx words in Quran
        // Wait, 'words' table is unique words. That's ~15k-19k.
        // Let's use unique words count.
        const res2 = DB.db.exec("SELECT COUNT(*) FROM words");
        const uniqueWords = res2[0].values[0][0];

        const percent = ((masteredCount / uniqueWords) * 100).toFixed(1);
        document.getElementById('user-mastery').textContent = `${percent}%`;
    },

    startSession() {
        this.sessionWords = DB.getDailyWords(10);
        if (this.sessionWords.length === 0) {
            alert(UI_TRANSLATIONS[this.currentLanguage].no_words);
            return;
        }

        this.currentWordIndex = 0;
        this.isFlipped = false;

        document.getElementById('dashboard-screen').classList.add('hidden');
        document.getElementById('game-screen').classList.remove('hidden');

        this.showCard();
    },

    showCard() {
        this.currentWord = this.sessionWords[this.currentWordIndex];
        this.isFlipped = false;

        const card = document.getElementById('flashcard');
        card.classList.remove('flipped');
        document.getElementById('game-controls').classList.add('hidden');

        document.getElementById('card-arabic').textContent = this.currentWord.arabic;
        // Language aware meaning
        const meaning = this.currentLanguage === 'bn' ? this.currentWord.bengali : this.currentWord.english;
        document.getElementById('card-english').textContent = meaning;

        document.getElementById('card-stats').textContent = `Freq: ${this.currentWord.frequency}`;

        const progressText = UI_TRANSLATIONS[this.currentLanguage].word_progress || "Word";
        document.getElementById('session-progress').textContent = `${progressText} ${this.currentWordIndex + 1}/${this.sessionWords.length}`;
    },

    flipCard() {
        if (this.isFlipped) return;
        this.isFlipped = true;
        document.getElementById('flashcard').classList.add('flipped');
        document.getElementById('game-controls').classList.remove('hidden');
    },

    async answerCard(rating) {
        if (!this.currentWord) return;

        // Calculate updates
        const currentStrength = this.currentWord.strength_level || 0;
        const reviewData = GameLogic.getNextReviewData(currentStrength, rating);
        const xpGain = GameLogic.calculateXP(rating);

        // Update DB
        DB.updateWordProgress(
            this.currentWord.id,
            rating === 'hard' ? 'learning' : 'mastered', // Simple status logic
            reviewData.nextReview,
            reviewData.newStrength
        );

        // Update Profile XP
        const profile = DB.getProfile();
        DB.updateProfile({ total_xp: profile.total_xp + xpGain });

        // Next card
        this.currentWordIndex++;
        if (this.currentWordIndex < this.sessionWords.length) {
            setTimeout(() => this.showCard(), 300); // slight delay for animation
        } else {
            this.endSession();
        }
    },

    endSession() {
        alert(UI_TRANSLATIONS[this.currentLanguage].session_complete);
        document.getElementById('game-screen').classList.add('hidden');
        document.getElementById('dashboard-screen').classList.remove('hidden');
        this.updateDashboard();
    },

    initSurahSelector() {
        const select = document.getElementById('surah-select');
        const selectedValue = select.value;
        select.innerHTML = '';

        const defaultOption = document.createElement('option');
        defaultOption.value = "";
        defaultOption.disabled = true;
        defaultOption.selected = true;
        defaultOption.textContent = UI_TRANSLATIONS[this.currentLanguage].choose_surah;
        select.appendChild(defaultOption);

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

        const names = this.currentLanguage === 'bn' ? SURAH_NAMES_BN : SURAH_NAMES;

        names.forEach((name, index) => {
            const option = document.createElement('option');
            option.value = index + 1;
            option.textContent = `Surah ${index + 1} (${name})`;
            select.appendChild(option);
        });

        if(selectedValue) {
            select.value = selectedValue;
        }

        // Only add listener once or check if it exists?
        // We are clearing innerHTML so options are new, but the element is same.
        // The listener is attached to the element in init(), so we should be careful not to attach duplicates if we call this multiple times.
        // Actually, initSurahSelector is called in applyLanguage.
        // So we should move the event listener attachment OUT of this function or ensure it's idempotent.
        // The event listener was attached in init() via initSurahSelector?
        // In my previous app.js code, initSurahSelector added the listener.
        // I will change it so initSurahSelector only populates options.
        // And setupEventListeners attaches the change event.
    },

    renderSurahDeck(surahId) {
        const words = DB.getWordsBySurah(surahId, 20);
        const container = document.getElementById('surah-deck');
        container.innerHTML = '';

        words.forEach((item, index) => {
            const card = this.createStaticCard(item, index + 1);
            container.appendChild(card);
        });
    },

    renderGlobalDeck() {
        const words = DB.getTopWords(50);
        const container = document.getElementById('global-deck');
        container.innerHTML = '';

        words.forEach((item, index) => {
            const card = this.createStaticCard(item, index + 1);
            container.appendChild(card);
        });
    },

    toBengaliNumerals(n) {
        const bnNums = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
        return n.toString().replace(/\d/g, d => bnNums[d]);
    },

    createStaticCard(item, rank) {
        // Reuse similar HTML structure but simpler for browsing
        const card = document.createElement('div');
        const surahFreqLabel = UI_TRANSLATIONS[this.currentLanguage].surah_freq;
        const globalFreqLabel = UI_TRANSLATIONS[this.currentLanguage].global_freq;

        const countDisplay = item.local_count !== undefined
            ? `${surahFreqLabel}: ${item.local_count}`
            : `${globalFreqLabel}: ${item.frequency}`;

        const meaning = this.currentLanguage === 'bn' ? item.bengali : item.english;
        const displayRank = this.currentLanguage === 'bn' ? this.toBengaliNumerals(rank) : rank;

        card.className = 'card';
        card.innerHTML = `
            <span class="badge">#${displayRank}</span>
            <div class="card-content">
                <div class="card-front">
                    <div class="arabic-word">${item.arabic}</div>
                </div>
                <div class="card-back">
                    <div class="english-meaning">${meaning}</div>
                    <div class="frequency-count">${countDisplay}</div>
                </div>
            </div>
        `;
        card.addEventListener('click', () => card.classList.toggle('revealed'));
        return card;
    },

    setupEventListeners() {
        // Navigation
        document.getElementById('nav-dashboard').addEventListener('click', () => {
            this.switchScreen('dashboard-screen');
            this.updateDashboard();
        });
        document.getElementById('nav-browse').addEventListener('click', () => {
            this.switchScreen('browse-screen');
            this.renderGlobalDeck();
        });

        // Game Start
        document.getElementById('start-session-btn').addEventListener('click', () => this.startSession());
        document.getElementById('quit-session').addEventListener('click', () => this.endSession());

        // Card Interaction
        document.getElementById('flashcard').addEventListener('click', () => this.flipCard());

        // Ratings
        document.querySelectorAll('.rating-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent card flip
                const rating = e.target.dataset.rating;
                this.answerCard(rating);
            });
        });

        // Surah Select
        document.getElementById('surah-select').addEventListener('change', (e) => {
            const surahId = parseInt(e.target.value);
            this.renderSurahDeck(surahId);
        });
    },

    switchScreen(screenId) {
        document.querySelectorAll('.screen').forEach(el => el.classList.add('hidden'));
        document.getElementById(screenId).classList.remove('hidden');

        // Update nav buttons
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        if (screenId === 'dashboard-screen') document.getElementById('nav-dashboard').classList.add('active');
        if (screenId === 'browse-screen') document.getElementById('nav-browse').classList.add('active');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
