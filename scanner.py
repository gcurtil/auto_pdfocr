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
    def __init__(self, input_dir: str):
        self.input_dir = Path(input_dir)

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
    def calculate_hash(file_path: Path) -> str:
        """
        Calculates the SHA-256 hash of a file.

        Parameters
        ----------
        file_path : Path
            The path to the file to hash.

        Returns
        -------
        str
            The hexadecimal representation of the SHA-256 hash.
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def scan(self) -> List[Tuple[Path, str]]:
        """
        Scans the directory and returns a list of (path, hash) tuples.

        Returns
        -------
        List[Tuple[Path, str]]
            A list of tuples, where each tuple contains the file path and its SHA-256 hash.
        """
        results = []
        for pdf_file in self.get_pdf_files():
            file_hash = self.calculate_hash(pdf_file)
            results.append((pdf_file, file_hash))
        return results
