# utils/ocr.py

import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image


def ocr_pdf_to_text(pdf_path: str, output_dir="hasil_teks") -> str:
    text_result = ""

    with fitz.open(pdf_path) as doc:
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img)
            text_result += text + "\n\n"

    os.makedirs(output_dir, exist_ok=True)
    
    base_name = os.path.basename(pdf_path).replace(".pdf", ".txt")
    txt_path = os.path.join(output_dir, base_name)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text_result)

    return text_result
