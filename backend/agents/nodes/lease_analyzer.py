import os
from langchain_openai import ChatOpenAI
from backend.api.schemas import LeaseAnalyzerResponse

def analyze_lease(file_name:str,lease_text: str) -> LeaseAnalyzerResponse:
    # 1. Define the LLM (You could also import a shared LLM instance if you create one)
    llm = ChatOpenAI(
        openai_api_key=os.getenv("openai_api_key"),
        openai_api_base="https://openrouter.ai/api/v1",
        model_name="openrouter/auto-beta",
    )
    
    # 2. Bind the structured output schema
    structured_llm = llm.with_structured_output(LeaseAnalyzerResponse)
    
    # 3. Create the prompt
    prompt = f"""
    You are a lease analyzer for this German tenant lease. 
    Document Filename: {file_name}
    
    Analyze and interpret the terms and clauses and return the analysis in a structured format, 
    and define if its Safe, Needs Review (Vague terms, strict pet rules, or minor maintenance clauses.) 
    or Red Flag: {lease_text}
    """
    
    # 4. Invoke and return the Pydantic object
    return structured_llm.invoke(prompt)
