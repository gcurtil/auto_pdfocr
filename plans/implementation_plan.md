# Auto PDF OCR Implementation Plan

## 1. System Setup & Prerequisites

### 1.1. System Dependencies
The following system tools are required:
- **Rclone**: For mounting OneDrive.
- **Tesseract OCR**: The engine used by `ocrmypdf`.
- **Ghostscript**: Required by `ocrmypdf`.

### 1.2. Rclone Configuration
You need to configure two remotes (or one remote with two aliases/paths) for OneDrive.

**Setup Instructions:**
1.  Run `rclone config`.
2.  Create a new remote (e.g., `onedrive`).
3.  Select `onedrive` storage type.
4.  Follow the interactive authentication flow (requires a browser).
5.  Once configured, verify access: `rclone lsd onedrive:`

### 1.3. Mounting Directories
We will use systemd mount units or a startup script to mount the directories.
*   **Input (Read-Only)**: `rclone mount onedrive:/path/to/input /mnt/pdf_input --read-only --daemon`
*   **Output (Read-Write)**: `rclone mount onedrive:/path/to/output /mnt/pdf_output --daemon`

*Note: For development, we can use local directories simulating these mounts.*

## 2. Application Architecture

### 2.1. Database (`database.py`)
SQLite database to track processed files.

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS processed_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_hash ON processed_files(file_hash);
```

### 2.2. File Processing Logic
1.  **Scanning**:
    - Iterate through files in the Input Directory.
    - Ignore non-PDF files.
2.  **Identification & Validation**:
    - Calculate SHA-256 hash of the file content.
    - **Check DB**: `SELECT 1 FROM processed_files WHERE file_hash = ?`.
    - **Check Output**: Verify if `ocr_{filename}` exists in Output Directory.
    - **Decision**:
        - If in DB: Skip (Already processed).
        - If Output exists AND NOT `--overwrite`: Skip (Output exists).
        - Else: Mark for processing.
3.  **Execution (if not `--dry-run`)**:
    - **OCR Processing**:
        - Use `ocrmypdf` API.
        - Input: Source file path.
        - Output: Temporary file path.
        - Options: `--force-ocr`, `--deskew`, etc.
    - **Output**:
        - Move/Copy temporary output file to Output Directory.
    - **Finalize**:
        - Insert record into DB.

### 2.3. CLI & Modes
- **Arguments**:
    - `--input-dir`: Path to input directory.
    - `--output-dir`: Path to output directory.
    - `--dry-run`: Print actions without executing.
    - `--overwrite`: Force reprocessing even if output exists.
    - `--daemon`: Run continuously (default is one-off).
- **Modes**:
    - **One-off**: Scan once, process identified files, exit.
    - **Daemon**: Loop with sleep interval.

## 3. Project Structure
```
auto_pdfocr/
├── main.py            # CLI entry point and orchestration
├── database.py        # SQLite interactions
├── scanner.py         # File scanning and hashing logic
├── processor.py       # ocrmypdf wrapper
├── .gitignore
├── pyproject.toml
└── README.md
```

## 4. Implementation Steps
1.  **Implement Database**: Create `database.py` with init and check/add functions.
2.  **Implement Scanner**: Create `scanner.py` to list files and hash them.
3.  **Implement Processor**: Create `processor.py` to run `ocrmypdf`.
4.  **Implement Main CLI**: Create `main.py` using `argparse` to handle flags, modes, and orchestration.
