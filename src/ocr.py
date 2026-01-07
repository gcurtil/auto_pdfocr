import pytesseract
from pdf2image import convert_from_path
import os

def pdf_to_ocr(pdf_path, output_txt):
    """
    Converts a PDF file to text using OCR.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return

    print(f"Converting {pdf_path} to images...")
    images = convert_from_path(pdf_path)
    
    full_text = ""
    for i, image in enumerate(images):
        print(f"Processing page {i+1}...")
        text = pytesseract.image_to_string(image)
        full_text += text + "\n\n"
        
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    print(f"OCR complete. Text saved to {output_txt}")

if __name__ == "__main__":
    print("Auto PDF OCR script initialized.")
