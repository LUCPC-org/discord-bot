CREATE TABLE IF NOT EXISTS leaderboard (
    discord_id TEXT PRIMARY KEY NOT NULL,
    kattis_username TEXT NOT NULL,
    original_points INTEGER NOT NULL,
    current_points INTEGER NOT NULL
)