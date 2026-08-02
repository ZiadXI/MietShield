from fastapi import APIRouter
from backend.agents.state import run_agent
from backend.api.schemas import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat",response_model=ChatResponse)
async def chat_endpoint(request:ChatRequest):
    response = run_agent(request.message)
    return ChatResponse(response=response)