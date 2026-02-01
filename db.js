// db.js - Handles SQLite connection, persistence, and queries

const DB_NAME = "quran_learning_v1";
const TSV_FILE = "quran_word_translation.tsv";

// Common particles to exclude from "High Frequency" deck
const STOP_WORDS = [
    "فِي", "ٱلَّذِينَ", "مِن", "مَا", "لَا", "وَلَا", "إِنَّ", "إِلَّا", "وَمَا", "أَن", "مِنَ", "عَلَىٰ", "ثُمَّ", "مِّن", "مِّنَ", "يَٰٓأَيُّهَا", "إِذَا"
];

const DB = {
    db: null,
    sql: null,

    async init() {
        // 1. Load SQL.js
        const config = {
            locateFile: filename => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/${filename}`
        };
        this.sql = await initSqlJs(config);

        // 2. Try loading existing DB from IndexedDB
        const savedDb = await this.loadFromIDB();

        if (savedDb) {
            console.log("Loaded DB from storage.");
            this.db = new this.sql.Database(new Uint8Array(savedDb));
        } else {
            console.log("Creating new DB...");
            this.db = new this.sql.Database();
            await this.createSchema();
            await this.populateFromTSV();
            await this.saveToIDB();
        }

        return true;
    },

    async createSchema() {
        this.db.run(`
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arabic TEXT,
                english TEXT,
                frequency INTEGER,
                surah_counts TEXT -- JSON string: {"1": 5, "2": 10}
            );

            CREATE TABLE IF NOT EXISTS user_progress (
                word_id INTEGER PRIMARY KEY,
                status TEXT DEFAULT 'new',
                next_review_date INTEGER DEFAULT 0,
                strength_level INTEGER DEFAULT 0,
                FOREIGN KEY(word_id) REFERENCES words(id)
            );

            CREATE TABLE IF NOT EXISTS gamification (
                id INTEGER PRIMARY KEY,
                total_xp INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                last_login_date TEXT
            );

            INSERT OR IGNORE INTO gamification (id, total_xp, current_streak, last_login_date) VALUES (1, 0, 0, '');
        `);
    },

    async populateFromTSV() {
        return new Promise((resolve, reject) => {
            Papa.parse(TSV_FILE, {
                download: true,
                header: true,
                delimiter: "\t",
                skipEmptyLines: true,
                complete: (results) => {
                    this.processAndInsertData(results.data);
                    resolve();
                },
                error: (err) => reject(err)
            });
        });
    },

    processAndInsertData(rows) {
        const wordMap = new Map();

        rows.forEach(row => {
            const word = row.ar;
            const meaning = row.en;
            const surahId = row.surah; // keep as string key

            if (!word) return;

            if (!wordMap.has(word)) {
                wordMap.set(word, {
                    arabic: word,
                    english: meaning, // Taking the first meaning found
                    count: 0,
                    surah_counts: {}
                });
            }

            const entry = wordMap.get(word);
            entry.count++;
            if (!entry.surah_counts[surahId]) {
                entry.surah_counts[surahId] = 0;
            }
            entry.surah_counts[surahId]++;
        });

        // Insert into DB
        this.db.run("BEGIN TRANSACTION");
        const stmt = this.db.prepare("INSERT INTO words (arabic, english, frequency, surah_counts) VALUES (?, ?, ?, ?)");

        for (const [key, val] of wordMap) {
            stmt.run([
                val.arabic,
                val.english,
                val.count,
                JSON.stringify(val.surah_counts)
            ]);
        }
        stmt.free();
        this.db.run("COMMIT");

        // Initialize Progress table for all words
        this.db.run(`
            INSERT INTO user_progress (word_id, status, next_review_date, strength_level)
            SELECT id, 'new', 0, 0 FROM words
        `);
    },

    // --- Persistence (IndexedDB) ---

    loadFromIDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, 1);
            request.onupgradeneeded = function(e) {
                const db = e.target.result;
                db.createObjectStore("store");
            };
            request.onsuccess = function(e) {
                const db = e.target.result;
                const tx = db.transaction("store", "readonly");
                const store = tx.objectStore("store");
                const getReq = store.get("sqliteFile");
                getReq.onsuccess = function() {
                    resolve(getReq.result);
                };
                getReq.onerror = function() {
                    resolve(null);
                };
            };
            request.onerror = function() {
                resolve(null);
            };
        });
    },

    async saveToIDB() {
        const data = this.db.export();
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, 1);
            request.onsuccess = function(e) {
                const db = e.target.result;
                const tx = db.transaction("store", "readwrite");
                const store = tx.objectStore("store");
                const putReq = store.put(data, "sqliteFile");
                putReq.onsuccess = resolve;
                putReq.onerror = reject;
            };
        });
    },

    // --- Queries ---

    getProfile() {
        const res = this.db.exec("SELECT * FROM gamification WHERE id = 1");
        if (res.length > 0 && res[0].values.length > 0) {
            const [id, total_xp, current_streak, last_login_date] = res[0].values[0];
            return { total_xp, current_streak, last_login_date };
        }
        return { total_xp: 0, current_streak: 0, last_login_date: '' };
    },

    updateProfile(updates) {
        // updates: { total_xp, current_streak, last_login_date }
        const current = this.getProfile();
        const xp = updates.total_xp !== undefined ? updates.total_xp : current.total_xp;
        const streak = updates.current_streak !== undefined ? updates.current_streak : current.current_streak;
        const login = updates.last_login_date !== undefined ? updates.last_login_date : current.last_login_date;

        this.db.run("UPDATE gamification SET total_xp = ?, current_streak = ?, last_login_date = ? WHERE id = 1", [xp, streak, login]);
        this.saveToIDB();
    },

    getDailyWords(limit = 10) {
        const now = Date.now();
        // Priority: Words due for review -> New words

        // Find due reviews
        let query = `
            SELECT w.*, p.status, p.next_review_date, p.strength_level
            FROM words w
            JOIN user_progress p ON w.id = p.word_id
            WHERE p.status IN ('learning', 'mastered') AND p.next_review_date <= ?
            ORDER BY w.frequency DESC
            LIMIT ?
        `;
        let res = this.db.exec(query, [now, limit]);
        let dueWords = [];
        if (res.length > 0) {
            dueWords = this.mapResults(res[0]);
        }

        if (dueWords.length >= limit) {
            return dueWords;
        }

        // Fill rest with new high-frequency words
        const remaining = limit - dueWords.length;

        query = `
            SELECT w.*, p.status, p.next_review_date, p.strength_level
            FROM words w
            JOIN user_progress p ON w.id = p.word_id
            WHERE p.status = 'new'
            ORDER BY w.frequency DESC
            LIMIT ?
        `;

        // We might need to fetch more to filter stop words in JS
        res = this.db.exec(query, [remaining + 20]);
        let newWords = [];
        if (res.length > 0) {
            newWords = this.mapResults(res[0]);
        }

        // Filter stop words from newWords
        newWords = newWords.filter(w => !STOP_WORDS.includes(w.arabic));

        return [...dueWords, ...newWords.slice(0, remaining)];
    },

    updateWordProgress(wordId, newStatus, nextReview, newStrength) {
        this.db.run(
            "UPDATE user_progress SET status = ?, next_review_date = ?, strength_level = ? WHERE word_id = ?",
            [newStatus, nextReview, newStrength, wordId]
        );
        this.saveToIDB();
    },

    getTopWords(limit = 50) {
        const query = `
            SELECT w.*
            FROM words w
            ORDER BY w.frequency DESC
            LIMIT ?
        `;
        // Fetch a bit more to handle stop word filtering in JS
        const res = this.db.exec(query, [limit + 20]);
        if (res.length === 0) return [];

        let words = this.mapResults(res[0]);
        return words.filter(w => !STOP_WORDS.includes(w.arabic)).slice(0, limit);
    },

    getWordsBySurah(surahId, limit = 20) {
        // We fetch ALL words, filter in JS. Not optimal for huge DBs, but fine for 70k rows?
        // We rely on the fact that `surah_counts` is a text field.
        const query = "SELECT * FROM words";
        const res = this.db.exec(query);
        if (res.length === 0) return [];

        const allWords = this.mapResults(res[0]);
        const surahStr = String(surahId);

        const filtered = [];
        for (const w of allWords) {
            if (STOP_WORDS.includes(w.arabic)) continue;

            const counts = JSON.parse(w.surah_counts);
            if (counts[surahStr]) {
                filtered.push({
                    ...w,
                    local_count: counts[surahStr]
                });
            }
        }

        // Sort by local count
        return filtered.sort((a, b) => b.local_count - a.local_count).slice(0, limit);
    },

    // Helper to map sql.js results to objects
    mapResults(res) {
        const columns = res.columns;
        return res.values.map(row => {
            const obj = {};
            columns.forEach((col, i) => {
                obj[col] = row[i];
            });
            return obj;
        });
    }
};
