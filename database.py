import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_path: str = "processed_files.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_hash TEXT NOT NULL UNIQUE,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_hash ON processed_files(file_hash)")

    def is_processed(self, file_hash: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM processed_files WHERE file_hash = ?", (file_hash,))
            return cursor.fetchone() is not None

    def mark_processed(self, filename: str, file_hash: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO processed_files (filename, file_hash) VALUES (?, ?)",
                (filename, file_hash)
            )
