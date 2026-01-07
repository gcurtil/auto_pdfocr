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


def _get_file_size(path: Path) -> int | None:
    """
    Safely fetches the size of a file in bytes.

    Parameters
    ----------
    path : Path
        File whose size should be read.

    Returns
    -------
    int or None
        Size in bytes if available; otherwise ``None`` when the stat call fails.
    """
    try:
        return path.stat().st_size
    except OSError as exc:  # noqa: BLE001
        logger.warning(f"Unable to read size for {path}: {exc}")
        return None


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
        try:
            file_hash: str = scanner.calculate_hash(
                pdf_path, retries=args.retries, retry_delay=args.retry_delay
            )
        except OSError as e:
            logger.error(f"Could not read {pdf_path.name} after retries: {e}. Skipping.")
            continue

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

    # Apply limit
    total_found: int = len(files_to_process)
    if args.limit > 0:
        files_to_process = files_to_process[: args.limit]

    logger.info(
        f"Found {total_found} new files. Processing {len(files_to_process)} "
        f"(limit: {args.limit})."
    )

    for pdf_path, file_hash in files_to_process:
        input_size = _get_file_size(pdf_path)
        result = processor.process(pdf_path, dry_run=args.dry_run)

        if result.success and not args.dry_run:
            db.mark_processed(
                filename=pdf_path.name,
                input_dir=str(scanner.input_dir),
                output_dir=str(processor.output_dir),
                file_hash=file_hash,
                input_size=input_size,
                output_size=result.output_size,
                duration=result.duration,
            )


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
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of files to process in one iteration (default: 5)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retries for file I/O errors (default: 3)",
    )
    parser.add_argument(
        "--retry-delay",
        type=int,
        default=5,
        help="Delay in seconds between retries (default: 5)",
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
