from pydantic import BaseModel, Field
from typing import Optional, List
from typing import Literal


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default_thread"  # Sent by the frontend per chat session

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None

class LeaseAnalyzerRequest(BaseModel):
    lease_text: str

    
class ClauseAnalysis(BaseModel):
    topic: str = Field(description="The general topic of the clause, e.g., 'Security Deposit', 'Pets', or 'Notice Period'.")
    extracted_text: str = Field(description="The exact quote from the lease PDF.")
    risk_score: Literal["Safe", "Review", "Red Flag"] = Field(description="Rate the legality of this clause based on German law.")
    explanation: str = Field(description="Explain in plain English why this clause received its risk score.")
    law_reference: str = Field(description="The specific German law (e.g., '§ 551 BGB') that applies, if any.")

class LeaseAnalyzerResponse(BaseModel):
    clauses: List[ClauseAnalysis] = Field(description="A list of all the clauses analyzed from the lease.")
    overall_summary: str = Field(description="A 2-sentence overall summary of the lease's legal health.")