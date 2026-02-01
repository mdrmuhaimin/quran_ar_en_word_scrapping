// game_logic.js - Handles XP, Levels, and Spaced Repetition Logic

const GameLogic = {
    // Check and update streak
    checkStreak(lastLoginDate) {
        const today = new Date().toISOString().split('T')[0];
        if (!lastLoginDate) return 1; // First day

        const last = new Date(lastLoginDate);
        const now = new Date(today);

        const diffTime = Math.abs(now - last);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 1) {
            return "increment"; // Login was yesterday
        } else if (diffDays > 1) {
            return "reset"; // Missed a day
        }
        return "same"; // Already logged in today
    },

    // Calculate XP based on difficulty rating
    calculateXP(rating) {
        switch (rating) {
            case 'easy': return 15;
            case 'good': return 10;
            case 'hard': return 5;
            default: return 0;
        }
    },

    // Calculate Level based on Total XP
    // Formula: Level = floor(sqrt(XP / 100)) + 1
    getLevel(xp) {
        return Math.floor(Math.sqrt(xp / 100)) + 1;
    },

    // Calculate progress for current level
    getLevelProgress(xp) {
        const level = this.getLevel(xp);
        const currentLevelXp = 100 * Math.pow(level - 1, 2);
        const nextLevelXp = 100 * Math.pow(level, 2);

        const progress = xp - currentLevelXp;
        const needed = nextLevelXp - currentLevelXp;

        return Math.min(100, Math.floor((progress / needed) * 100));
    },

    // Simple SRS Algorithm
    // Rating: 'hard' (0), 'good' (1), 'easy' (2)
    // Strength: 0-5
    getNextReviewData(currentStrength, rating) {
        let newStrength = currentStrength;
        let daysToAdd = 0;

        if (rating === 'hard') {
            newStrength = Math.max(0, currentStrength - 1);
            daysToAdd = 0; // Review immediately/tomorrow
        } else if (rating === 'good') {
            newStrength = Math.min(5, currentStrength + 1);
            daysToAdd = Math.pow(2, newStrength); // 2, 4, 8, 16...
        } else if (rating === 'easy') {
            newStrength = Math.min(5, currentStrength + 2);
            daysToAdd = Math.pow(2.5, newStrength); // Aggressive increase
        }

        const nextDate = new Date();
        nextDate.setDate(nextDate.getDate() + Math.floor(daysToAdd));

        return {
            nextReview: nextDate.getTime(),
            newStrength: newStrength
        };
    }
};
