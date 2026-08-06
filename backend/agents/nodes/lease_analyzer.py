from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.api.schemas import LeaseAnalyzerResponse

# =====================================================================
# BRAINSTORMING & CREATIVE GUIDELINES FOR LEASE ANALYZER NODE
# =====================================================================
# Your Goal: Take the raw text extracted from a lease PDF and use an LLM
# to return a structured `LeaseAnalyzerResponse`.
#
# Key Creative Decisions for You to Make:
# 1. System Persona: How should the AI introduce itself? 
#    (e.g., "You are an expert German tenant law consultant...")
# 2. Guidelines for Risk Ratings:
#    - What defines a "Red Flag"? (e.g., Illegal deposit > 3 months rent, tenant pays repairs over €100).
#    - What defines a "Review"? (e.g., Strict pet restrictions, vague notice periods).
#    - What defines "Safe"? (e.g., Standard legal clauses per BGB).
# 3. Prompt Layout: How do you structure the input so the LLM focuses on
#    extracting real text quotes and citing specific German laws (§ BGB)?
# =====================================================================

def analyze_lease(lease_text: str) -> LeaseAnalyzerResponse:
    """
    Analyzes raw lease text and returns a structured Pydantic response.
    
    TODO: 
    1. Initialize the ChatOpenAI model (e.g., model="gpt-4o-mini" or "gpt-4o", temperature=0.0).
    2. Bind the schema using `model.with_structured_output(LeaseAnalyzerResponse)`.
    3. Craft your system prompt and human prompt using `ChatPromptTemplate`.
    4. Invoke the chain with `lease_text` and return the structured response!
    """
    # Write your implementation here!
    pass
