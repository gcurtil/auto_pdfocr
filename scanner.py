import hashlib
from pathlib import Path
from typing import List, Tuple

class Scanner:
    def __init__(self, input_dir: str):
        self.input_dir = Path(input_dir)

    def get_pdf_files(self) -> List[Path]:
        """Returns a list of PDF files in the input directory."""
        if not self.input_dir.exists():
            return []
        return list(self.input_dir.glob("*.pdf"))

    @staticmethod
    def calculate_hash(file_path: Path) -> str:
        """Calculates the SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def scan(self) -> List[Tuple[Path, str]]:
        """Scans the directory and returns a list of (path, hash) tuples."""
        results = []
        for pdf_file in self.get_pdf_files():
            file_hash = self.calculate_hash(pdf_file)
            results.append((pdf_file, file_hash))
        return results
