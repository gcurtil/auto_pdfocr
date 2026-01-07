# Auto PDF OCR

Auto PDF OCR is a lightweight, automated tool designed to scan a directory for PDF files, perform OCR (Optical Character Recognition) on them using `ocrmypdf`, and save the searchable PDFs to an output directory. It uses content hashing to ensure that identical files are not processed multiple times, even if their filenames change.

## Features

- **Automated Scanning**: Monitors an input directory for PDF files.
- **Smart Processing**: Uses SHA-256 content hashing to track processed files, preventing redundant OCR operations.
- **OCR Integration**: Leverages `ocrmypdf` to add a text layer to scanned PDFs, making them searchable and selectable.
- **Daemon Mode**: Can run continuously in the background, polling for new files at a specified interval.
- **Flexible Configuration**: Customizable input/output directories and polling intervals.
- **Dry Run**: Simulate processing to see what would happen without making changes.

## Prerequisites

Before running the tool, ensure you have the following installed:

### System Dependencies

- **Python 3.13+**
- **Tesseract OCR**: The OCR engine.
- **Ghostscript**: Required by `ocrmypdf`.
- **Rclone** (Optional): If you plan to mount cloud storage (e.g., OneDrive) as your input/output directories.

On Debian/Ubuntu-based systems, you can install the required tools via:

```bash
sudo apt update
sudo apt install tesseract-ocr ghostscript python3-pip
```

### Python Dependencies

The project uses `ocrmypdf` and standard libraries. Install the dependencies using pip:

```bash
pip install ocrmypdf
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd auto_pdfocr
   ```

2. Install the package (editable mode recommended for development):
   ```bash
   pip install -e .
   ```

## Usage

The tool is run via the `main.py` script.

### Basic Command

```bash
python main.py --input-dir /path/to/input --output-dir /path/to/output
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--input-dir` | Directory to scan for PDF files (Required). | - |
| `--output-dir` | Directory to save OCR'd PDF files (Required). | - |
| `--db-path` | Path to the SQLite database for tracking processed files. | `processed_files.db` |
| `--dry-run` | Simulate processing without executing OCR or modifying the DB. | `False` |
| `--overwrite` | Force reprocessing even if the output file already exists. | `False` |
| `--daemon` | Run continuously in a loop. | `False` |
| `--interval` | Polling interval in seconds (only for daemon mode). | `60` |

### Examples

**1. One-off run:**
Scan the `inbox` directory and save OCR'd files to `archive`.
```bash
python main.py --input-dir ./inbox --output-dir ./archive
```

**2. Daemon mode:**
Run continuously, checking for new files every 5 minutes (300 seconds).
```bash
python main.py --input-dir ./inbox --output-dir ./archive --daemon --interval 300
```

**3. Dry run:**
Check which files would be processed without actually doing it.
```bash
python main.py --input-dir ./inbox --output-dir ./archive --dry-run
```

## Project Structure

- `main.py`: Entry point and orchestration logic.
- `database.py`: Handles SQLite database interactions for tracking file hashes.
- `scanner.py`: Scans directories and calculates file hashes.
- `processor.py`: Wrapper around `ocrmypdf` for executing OCR.
- `plans/`: Contains implementation plans and documentation.

## Database

The tool maintains a SQLite database (`processed_files.db` by default) to keep track of processed files. This ensures that if you move or rename a source file that has already been processed, the tool will recognize it by its content hash and skip it.
