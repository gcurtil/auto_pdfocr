"""
Database management for the Auto PDF OCR tool.

This module provides the Database class to handle SQLite interactions,
tracking processed files by their content hashes.
"""

import sqlite3
from pathlib import Path


class Database:
    """
    Manages the SQLite database for tracking processed files.

    Parameters
    ----------
    db_path : str, optional
        The path to the SQLite database file (default is "processed_files.db").
    """

    def __init__(self, db_path: str = "processed_files.db") -> None:
        self.db_path: str = db_path
        self._init_db()

    def _init_db(self) -> None:
        """
        Initializes the database table and index if they don't exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_hash TEXT NOT NULL UNIQUE,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_hash ON processed_files(file_hash)"
            )

    def is_processed(self, file_hash: str) -> bool:
        """
        Checks if a file with the given hash has already been processed.

        Parameters
        ----------
        file_hash : str
            The SHA-256 hash of the file.

        Returns
        -------
        bool
            True if the file hash exists in the database, False otherwise.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM processed_files WHERE file_hash = ?", (file_hash,)
            )
            return cursor.fetchone() is not None

    def mark_processed(self, filename: str, file_hash: str) -> None:
        """
        Marks a file as processed by inserting it into the database.

        Parameters
        ----------
        filename : str
            The name of the file.
        file_hash : str
            The SHA-256 hash of the file.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO processed_files (filename, file_hash) VALUES (?, ?)",
                (filename, file_hash),
            )
