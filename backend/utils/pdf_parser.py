import fitz  # PyMuPDF


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Takes raw PDF bytes, extracts all text, and returns it as a single string.
    If the PDF is a scanned image, falls back to OCR.
    """
    full_text = ""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    try:
        # Step 1: Try digital text extraction first (fast pass)
        for page in doc:
            text = page.get_text()
            if text:
                full_text += text + "\n"
                
        # Step 2: If digital extraction failed, fall back to OCR
        if not full_text.strip():
            from rapidocr_onnxruntime import RapidOCR  # Lazy import — only loads if needed
            engine = RapidOCR()
            for page in doc:
                pix = page.get_pixmap(dpi=300)
                # Convert pixmap directly to bytes in memory (no disk file created)
                img_bytes = pix.tobytes("png")
                
                # Perform OCR on image bytes
                result, _ = engine(img_bytes)
                if result:
                    # Extract text lines from OCR result tuple
                    ocr_text = "\n".join([line[1] for line in result])
                    full_text += ocr_text + "\n"
                    
    finally:
        doc.close()  # Guaranteed memory cleanup
        
    if not full_text.strip():
        raise ValueError("Could not extract text from PDF (file may be blank or corrupted).")
        
    return full_text
