"""
Main entry point for the Auto PDF OCR tool.

This script orchestrates the scanning of an input directory for PDF files,
checking them against a database of processed files, and running OCR
on new or modified files.
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import List, Tuple

from database import Database
from processor import Processor
from scanner import Scanner


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def run_once(
    args: argparse.Namespace, db: Database, scanner: Scanner, processor: Processor
) -> None:
    """
    Performs a single scan and process cycle.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.
    db : Database
        The database instance.
    scanner : Scanner
        The scanner instance.
    processor : Processor
        The processor instance.
    """
    logger.info(f"Scanning {args.input_dir}...")
    files_to_process: List[Tuple[Path, str]] = []

    pdf_files: List[Path] = scanner.get_pdf_files()
    if not pdf_files:
        logger.info("No PDF files found.")
        return

    for pdf_path in pdf_files:
        file_hash: str = scanner.calculate_hash(pdf_path)
        output_path: Path = processor.get_output_path(pdf_path)

        # Check DB
        if db.is_processed(file_hash):
            logger.debug(f"Skipping {pdf_path.name}: Already in database.")
            continue

        # Check Output existence
        if output_path.exists() and not args.overwrite:
            logger.info(
                f"Skipping {pdf_path.name}: Output file already exists "
                "(use --overwrite to force)."
            )
            continue

        files_to_process.append((pdf_path, file_hash))

    if not files_to_process:
        logger.info("No new files to process.")
        return

    logger.info(f"Found {len(files_to_process)} new files to process.")

    for pdf_path, file_hash in files_to_process:
        success: bool = processor.process(pdf_path, dry_run=args.dry_run)
        if success and not args.dry_run:
            db.mark_processed(pdf_path.name, file_hash)


def main() -> None:
    """
    Main entry point for the Auto PDF OCR tool.

    Parses arguments and orchestrates the scanning and processing loop.
    """
    parser = argparse.ArgumentParser(description="Auto PDF OCR Tool")
    parser.add_argument(
        "--input-dir", required=True, help="Directory to scan for PDF files"
    )
    parser.add_argument(
        "--output-dir", required=True, help="Directory to save OCR'd PDF files"
    )
    parser.add_argument(
        "--db-path", default="processed_files.db", help="Path to SQLite database"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate processing without making changes",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files in output directory",
    )
    parser.add_argument(
        "--daemon", action="store_true", help="Run in daemon mode (continuous polling)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Polling interval in seconds (daemon mode only)",
    )

    args: argparse.Namespace = parser.parse_args()

    # Initialize components
    db = Database(args.db_path)
    scanner = Scanner(args.input_dir)
    processor = Processor(args.output_dir)

    if args.daemon:
        logger.info(f"Starting daemon mode (interval: {args.interval}s)...")
        try:
            while True:
                run_once(args, db, scanner, processor)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Daemon stopped by user.")
    else:
        run_once(args, db, scanner, processor)
        logger.info("One-off run completed.")


if __name__ == "__main__":
    main()
