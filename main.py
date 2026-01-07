import argparse
import time
import logging
import sys
from pathlib import Path
from database import Database
from scanner import Scanner
from processor import Processor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def run_once(args, db, scanner, processor):
    """Performs a single scan and process cycle."""
    logger.info(f"Scanning {args.input_dir}...")
    files_to_process = []
    
    pdf_files = scanner.get_pdf_files()
    if not pdf_files:
        logger.info("No PDF files found.")
        return

    for pdf_path in pdf_files:
        file_hash = scanner.calculate_hash(pdf_path)
        output_path = processor.get_output_path(pdf_path)
        
        # Check DB
        if db.is_processed(file_hash):
            logger.debug(f"Skipping {pdf_path.name}: Already in database.")
            continue
            
        # Check Output existence
        if output_path.exists() and not args.overwrite:
            logger.info(f"Skipping {pdf_path.name}: Output file already exists (use --overwrite to force).")
            continue
            
        files_to_process.append((pdf_path, file_hash))

    if not files_to_process:
        logger.info("No new files to process.")
        return

    logger.info(f"Found {len(files_to_process)} new files to process.")
    
    for pdf_path, file_hash in files_to_process:
        success = processor.process(pdf_path, dry_run=args.dry_run)
        if success and not args.dry_run:
            db.mark_processed(pdf_path.name, file_hash)

def main():
    parser = argparse.ArgumentParser(description="Auto PDF OCR Tool")
    parser.add_argument("--input-dir", required=True, help="Directory to scan for PDF files")
    parser.add_argument("--output-dir", required=True, help="Directory to save OCR'd PDF files")
    parser.add_argument("--db-path", default="processed_files.db", help="Path to SQLite database")
    parser.add_argument("--dry-run", action="store_true", help="Simulate processing without making changes")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files in output directory")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode (continuous polling)")
    parser.add_argument("--interval", type=int, default=60, help="Polling interval in seconds (daemon mode only)")

    args = parser.parse_args()

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
