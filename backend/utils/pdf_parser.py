import fitz  # PyMuPDF

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Takes raw PDF bytes, extracts all text, and returns it as a single string.
    """
    full_text = ""
    
    # Open the document using the stream of bytes
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    # Loop through the pages and extract text
    for page in doc:
        text = page.get_text()
        if text:
            full_text += text + "\n"
            
    doc.close()
    
    # Simple check if the PDF was an image without embedded text
    if not full_text.strip():
        raise ValueError("Could not extract any text from the PDF. It might be a scanned image.")
        
    return full_text