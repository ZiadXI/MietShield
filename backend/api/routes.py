import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.agents.state import run_agent
from backend.utils.pdf_parser import extract_text_from_pdf
from backend.agents.nodes.lease_analyzer import analyze_lease

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(
    message: str = Form(""),
    thread_id: str = Form("default_thread"),
    file: UploadFile = File(None)
):
    """
    Main conversational endpoint.
    Handles optional PDF lease uploads combined with user text prompts.
    
    PRODUCTION NOTE:
    - Thread validation: Currently blindly trusts the thread_id from the client.
      In a real production app, validate thread ownership against an authenticated user.
    - File size limits: Ensure the web server (Nginx/Uvicorn) limits request sizes 
      to prevent DOS attacks via massive PDF uploads.
    """
    try:
        combined_message = message
        
        # If a file is attached, process it and combine it with the user message
        if file:
            if not file.filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Only PDF files allowed")
                
            # PRODUCTION NOTE:
            # For large files, it is safer to save to a temporary file on disk 
            # rather than loading the entire file bytes into memory. 
            # For MVP, memory read is sufficient.
            file_bytes = await file.read()
            lease_text = extract_text_from_pdf(file_bytes)
            
            # Analyze lease
            analysis = analyze_lease(file_name=file.filename, lease_text=lease_text)
            
            # Format analysis into markdown for the prompt
            analysis_md = f"**Lease Document Analyzed: {file.filename}**\n\n"
            analysis_md += "Here is the AI's preliminary clause analysis (Risk Assessment):\n"
            for clause in analysis.clauses:
                risk_emoji = "🔴" if clause.risk_score == "Red Flag" else "🟡" if clause.risk_score == "Review" else "🟢"
                analysis_md += f"- {risk_emoji} **{clause.topic}**: {clause.explanation} (Ref: {clause.law_reference})\n"
            
            # Prepend context to the user's message
            combined_message = (
                f"[System Context: The user has attached a lease document. Analyze it and address their prompt.]\n\n"
                f"{analysis_md}\n\n"
                f"[Lease Text Begin]\n{lease_text}\n[Lease Text End]\n\n"
                f"User Message: {message if message else 'Please summarize the red flags in this lease.'}"
            )
            
        # Run agent
        response = run_agent(combined_message, thread_id=thread_id)
        return {"response": response}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))