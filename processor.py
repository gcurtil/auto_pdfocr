import ocrmypdf
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Processor:
    """
    Handles the OCR processing of PDF files.

    Parameters
    ----------
    output_dir : str
        The directory where processed files will be saved.
    """
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
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

    def process(self, input_path: Path, dry_run: bool = False) -> bool:
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
        bool
            True if processing was successful (or simulated), False otherwise.
        """
        output_path = self.get_output_path(input_path)
        
        if dry_run:
            logger.info(f"[DRY-RUN] Would process {input_path} -> {output_path}")
            return True

        try:
            logger.info(f"Processing {input_path}...")
            # ocrmypdf.ocr returns an exit code or raises an exception
            # We use some common flags: deskew, clean, rotate-pages
            ocrmypdf.ocr(
                input_path, 
                output_path, 
                deskew=True, 
                rotate_pages=True,
                # skip_text=True, # Use this if you only want to OCR images and keep existing text
                force_ocr=True,   # Use this if you want to force OCR even if text exists
                progress_bar=False
            )
            logger.info(f"Successfully processed {input_path}")
            return True
        except Exception as e:
            logger.error(f"Error processing {input_path}: {e}")
            return False
