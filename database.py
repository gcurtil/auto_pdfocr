"""
Database management for the Auto PDF OCR tool.

This module provides the Database class to handle SQLite interactions,
tracking processed files by their content hashes and associated metadata.
"""

from __future__ import annotations

import sqlite3
from typing import Dict

from ulid import ULID


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
        """Initializes and migrates the database schema if needed."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            self._ensure_schema(conn)

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        columns = self._get_table_info(conn)
        if not columns:
            self._create_fresh_schema(conn)
            return

        if self._requires_rebuild(columns):
            self._rebuild_table(conn)
            return

        self._add_missing_columns(conn, columns)
        self._create_indexes(conn)

    def _create_fresh_schema(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_files (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                input_dir TEXT NOT NULL,
                output_dir TEXT NOT NULL,
                file_hash TEXT NOT NULL UNIQUE,
                input_size INTEGER,
                output_size INTEGER,
                duration REAL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self._create_indexes(conn)

    @staticmethod
    def _create_indexes(conn: sqlite3.Connection) -> None:
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_hash ON processed_files(file_hash)"
        )

    def _rebuild_table(self, conn: sqlite3.Connection) -> None:
        rows = conn.execute("SELECT * FROM processed_files").fetchall()
        snapshot = [dict(row) for row in rows]

        conn.execute("DROP TABLE processed_files")
        self._create_fresh_schema(conn)

        insert_sql = (
            """
            INSERT INTO processed_files (
                id,
                filename,
                input_dir,
                output_dir,
                file_hash,
                input_size,
                output_size,
                duration,
                processed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        )

        for record in snapshot:
            conn.execute(
                insert_sql,
                (
                    ULID().str,
                    record.get("filename", ""),
                    record.get("input_dir", ""),
                    record.get("output_dir", ""),
                    record.get("file_hash", ""),
                    record.get("input_size"),
                    record.get("output_size"),
                    record.get("duration"),
                    record.get("processed_at"),
                ),
            )

    def _add_missing_columns(
        self, conn: sqlite3.Connection, existing: Dict[str, Dict[str, object]]
    ) -> None:
        column_specs = {
            "input_dir": "TEXT NOT NULL DEFAULT ''",
            "output_dir": "TEXT NOT NULL DEFAULT ''",
            "input_size": "INTEGER",
            "output_size": "INTEGER",
            "duration": "REAL",
        }

        for column, ddl in column_specs.items():
            if column not in existing:
                conn.execute(
                    f"ALTER TABLE processed_files ADD COLUMN {column} {ddl}"
                )

    @staticmethod
    def _requires_rebuild(columns: Dict[str, Dict[str, object]]) -> bool:
        id_column = columns.get("id")
        if id_column is None:
            return True
        column_type = str(id_column.get("type", "")).upper()
        return column_type != "TEXT"

    @staticmethod
    def _get_table_info(
        conn: sqlite3.Connection,
    ) -> Dict[str, Dict[str, object]]:
        cursor = conn.execute("PRAGMA table_info(processed_files)")
        info: Dict[str, Dict[str, object]] = {}
        for cid, name, col_type, notnull, default, pk in cursor.fetchall():
            info[name] = {
                "type": col_type,
                "notnull": notnull,
                "default": default,
                "pk": pk,
            }
        return info

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
                "SELECT 1 FROM processed_files WHERE file_hash = ?",
                (file_hash,),
            )
            return cursor.fetchone() is not None

    def mark_processed(
        self,
        filename: str,
        input_dir: str,
        output_dir: str,
        file_hash: str,
        input_size: int | None,
        output_size: int | None,
        duration: float | None,
    ) -> None:
        """
        Marks a file as processed by inserting it into the database.

        Parameters
        ----------
        filename : str
            The name of the file.
        input_dir : str
            Directory scanned for PDF files.
        output_dir : str
            Directory where OCR output is stored.
        file_hash : str
            The SHA-256 hash of the file.
        input_size : int or None
            Size of the input file in bytes, if available.
        output_size : int or None
            Size of the OCR output file in bytes, if available.
        duration : float or None
            Time spent (in seconds) performing OCR.
        """
        record_id = ULID().str
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO processed_files (
                    id,
                    filename,
                    input_dir,
                    output_dir,
                    file_hash,
                    input_size,
                    output_size,
                    duration
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    filename,
                    input_dir,
                    output_dir,
                    file_hash,
                    input_size,
                    output_size,
                    duration,
                ),
            )
