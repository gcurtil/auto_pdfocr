"""
File scanning and hashing logic for the Auto PDF OCR tool.

This module provides the Scanner class to identify PDF files in a directory
and calculate their SHA-256 content hashes.
"""

import hashlib
from pathlib import Path
from typing import List, Tuple


class Scanner:
    """
    Scans directories for PDF files and calculates their hashes.

    Parameters
    ----------
    input_dir : str
        The path to the directory to scan.
    """

    def __init__(self, input_dir: str) -> None:
        self.input_dir: Path = Path(input_dir)

    def get_pdf_files(self) -> List[Path]:
        """
        Returns a list of PDF files in the input directory.

        Returns
        -------
        List[Path]
            A list of paths to PDF files found in the input directory.
        """
        if not self.input_dir.exists():
            return []
        return list(self.input_dir.glob("*.pdf"))

    @staticmethod
    def calculate_hash(
        file_path: Path, retries: int = 0, retry_delay: int = 5
    ) -> str:
        """
        Calculates the SHA-256 hash of a file with optional retries.

        Parameters
        ----------
        file_path : Path
            The path to the file to hash.
        retries : int, optional
            Number of times to retry reading the file on OSError (default is 0).
        retry_delay : int, optional
            Seconds to wait between retries (default is 5).

        Returns
        -------
        str
            The hexadecimal representation of the SHA-256 hash.

        Raises
        ------
        OSError
            If the file cannot be read after all retry attempts.
        """
        import time

        attempt = 0
        while True:
            sha256_hash = hashlib.sha256()
            try:
                with open(file_path, "rb") as f:
                    # Read in chunks to handle large files
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                return sha256_hash.hexdigest()
            except OSError as e:
                attempt += 1
                if attempt > retries:
                    raise e
                time.sleep(retry_delay)

    def scan(self) -> List[Tuple[Path, str]]:
        """
        Scans the directory and returns a list of (path, hash) tuples.

        Returns
        -------
        List[Tuple[Path, str]]
            A list of tuples, where each tuple contains the file path and its SHA-256 hash.
        """
        results: List[Tuple[Path, str]] = []
        for pdf_file in self.get_pdf_files():
            file_hash = self.calculate_hash(pdf_file)
            results.append((pdf_file, file_hash))
        return results
