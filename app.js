const App = {
    // State
    sessionWords: [],
    currentWordIndex: 0,
    currentWord: null,
    isFlipped: false,

    async init() {
        console.log("App initializing...");
        try {
            await DB.init();

            // Check streak on login
            this.handleLogin();

            this.updateDashboard();
            this.setupEventListeners();

            // Switch to dashboard
            document.getElementById('loading-screen').classList.add('hidden');
            document.getElementById('dashboard-screen').classList.remove('hidden');

            // Initialize Browse Dropdown
            this.initSurahSelector();

        } catch (e) {
            console.error("Initialization failed:", e);
            document.getElementById('loading-text').textContent = "Error: " + e.message;
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
            alert("No words available! Database empty?");
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
        document.getElementById('card-english').textContent = this.currentWord.english;
        document.getElementById('card-stats').textContent = `Freq: ${this.currentWord.frequency}`;

        document.getElementById('session-progress').textContent = `Word ${this.currentWordIndex + 1}/${this.sessionWords.length}`;
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
        alert("Session Complete! Great job.");
        document.getElementById('game-screen').classList.add('hidden');
        document.getElementById('dashboard-screen').classList.remove('hidden');
        this.updateDashboard();
    },

    initSurahSelector() {
        const select = document.getElementById('surah-select');
        // Reuse the list from original script.js or DB?
        // Let's copy the list here to avoid global pollution or import issues
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

        SURAH_NAMES.forEach((name, index) => {
            const option = document.createElement('option');
            option.value = index + 1;
            option.textContent = `Surah ${index + 1} (${name})`;
            select.appendChild(option);
        });

        select.addEventListener('change', (e) => {
            const surahId = parseInt(e.target.value);
            this.renderSurahDeck(surahId);
        });
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

    createStaticCard(item, rank) {
        // Reuse similar HTML structure but simpler for browsing
        const card = document.createElement('div');
        const countDisplay = item.local_count !== undefined
            ? `Surah Freq: ${item.local_count}`
            : `Global Freq: ${item.frequency}`;

        card.className = 'card';
        card.innerHTML = `
            <span class="badge">#${rank}</span>
            <div class="card-content">
                <div class="card-front">
                    <div class="arabic-word">${item.arabic}</div>
                </div>
                <div class="card-back">
                    <div class="english-meaning">${item.english}</div>
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
