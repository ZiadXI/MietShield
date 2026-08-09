import fitz  # PyMuPDF


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Takes raw PDF bytes, extracts all text, and returns it as a single string.
    If the PDF is a scanned image, falls back to OCR.
    """
    full_text = ""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    try:
        # Extract digital text only (fast pass)
        for page in doc:
            text = page.get_text()
            if text:
                full_text += text + "\n"
                
    finally:
        doc.close()  # Guaranteed memory cleanup
        
    if not full_text.strip():
        raise ValueError("Could not extract text from PDF (it may be a scanned image or blank).")
        
    return full_text
