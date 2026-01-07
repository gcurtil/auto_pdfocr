"""
OCR processing logic for the Auto PDF OCR tool.

This module provides the Processor class to execute OCR on PDF files
using the ocrmypdf library.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path

import ocrmypdf


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ProcessResult:
    """Represents the outcome of processing a single PDF file."""

    success: bool
    duration: float
    output_size: int | None


class Processor:
    """
    Handles the OCR processing of PDF files.

    Parameters
    ----------
    output_dir : str
        The directory where processed files will be saved.
    """

    def __init__(self, output_dir: str) -> None:
        self.output_dir: Path = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_output_path(self, input_path: Path) -> Path:
        """
        Constructs the output path with 'ocr_' prefix.

        Parameters
        ----------
        input_path : Path
            The path of the input file.

        Returns
        -------
        Path
            The corresponding output path.
        """
        return self.output_dir / f"ocr_{input_path.name}"

    def process(self, input_path: Path, dry_run: bool = False) -> ProcessResult:
        """
        Runs OCR on the input file and saves it to the output directory.

        Parameters
        ----------
        input_path : Path
            The path to the PDF file to process.
        dry_run : bool, optional
            If True, simulates the processing without executing it (default is False).

        Returns
        -------
        ProcessResult
            A dataclass describing whether processing succeeded, how long it
            took, and the size of the resulting file (if applicable).
        """
        output_path: Path = self.get_output_path(input_path)

        if dry_run:
            logger.info(f"[DRY-RUN] Would process {input_path} -> {output_path}")
            return ProcessResult(success=True, duration=0.0, output_size=None)

        start_time = time.perf_counter()
        try:
            logger.info(f"Processing {input_path}...")
            ocrmypdf.ocr(
                input_path,
                output_path,
                deskew=True,
                rotate_pages=True,
                force_ocr=True,
                progress_bar=False,
            )
            duration = time.perf_counter() - start_time
            try:
                output_size = output_path.stat().st_size
            except OSError:
                output_size = None
            logger.info(f"Successfully processed {input_path} in {duration:.2f}s")
            return ProcessResult(True, duration, output_size)
        except Exception as exc:  # noqa: BLE001
            duration = time.perf_counter() - start_time
            logger.error(f"Error processing {input_path}: {exc}")
            return ProcessResult(False, duration, None)
