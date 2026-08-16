import os
from typing import Dict, TypedDict,List
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage # Message for providing instructions to the LLM
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langgraph.prebuilt import tools_condition
from backend.utils.pdf_parser import extract_text_from_pdf
from backend.api.schemas import LeaseAnalyzerResponse
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Annotated
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List,add_messages]
    user_info: str
    lease_text: str


# Initialize FAISS Vector Database at startup
file_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "german_law.md")
loader = TextLoader(file_path, encoding="utf-8")
docs = loader.load()
chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = FAISS.from_documents(chunks, embeddings)
retriever = vector_db.as_retriever(search_kwargs={"k": 3})

def retrieve_law(query: str) -> str:
    retrieved_docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in retrieved_docs])

@tool
def search_law(query: str):
    """Call this tool to search the German Tenancy Law database for rules and regulations. Input should be a specific search query."""
    return retrieve_law(query)

tools = [search_law]

llm = ChatOpenAI(
    openai_api_key=os.getenv("openai_api_key"),
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="openrouter/auto-beta",  # Vercel timeout warning: If this model is too slow, Vercel will time out.
).bind_tools(tools)

def model_call(state:AgentState)->AgentState:
      prompt_text = """You are MietShield, a friendly, empathetic, and professional AI legal assistant specializing in German Tenant Law (Mietrecht).
      
Your goal is to help tenants understand their rights and protect them from unfair landlord practices.

BEHAVIOR GUIDELINES:
1. Tone: Be warm, empathetic, and conversational. If the user greets you or introduces themselves, greet them back warmly by name before diving into legal topics. Do not sound like a rigid robot.
2. Tool Usage: If the user asks a specific question about German law (e.g., deposits, notice periods, pets, repairs), you MUST use the `search_law` tool to find the correct legal basis before answering.
3. Casual Chat: If the user is just saying hello, asking how you are, or making small talk, DO NOT use the `search_law` tool. Just chat normally and warmly.
4. Disclaimer: Occasionally remind users that you provide AI-assisted legal information, not formal legal representation.
5. File Analysis: If the user attaches a lease document, you will receive a structured analysis of its clauses along with the full text. Incorporate this analysis into your response, explaining the key red flags to the user clearly. You do not need to restate the entire lease, just summarize the important legal risks and answer the user's specific question.
6. Stay On Topic: You are STRICTLY a German Tenant Law assistant. If the user asks about off-topic subjects (like cooking recipes, programming, general history, or anything unrelated to renting in Germany), politely decline to answer and steer the conversation back to tenant law. Do not indulge off-topic requests.
7. Conciseness (CRITICAL): Keep your answers EXTREMELY BRIEF and to the point. Do not write long paragraphs, do not over-explain, and do not provide unsolicited advice. Give the user exactly what they asked for in the shortest way possible. Use bullet points to break up information.

Always format your responses cleanly using markdown (bullet points, bold text) to make complex legal concepts easy to read."""
      
      system_prompt = SystemMessage(content=prompt_text)
      response = llm.invoke([system_prompt]+state["messages"])
      return {"messages":response}
    
    
graph = StateGraph(AgentState)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.add_node("model_call",model_call)
graph.add_edge(START,"model_call")

graph.add_conditional_edges("model_call", tools_condition)

graph.add_edge("tools", "model_call")


# Create or open the SQLite database file
# PRODUCTION NOTE: SQLite is great for local prototyping. 
# For true production with multiple concurrent users, replace SqliteSaver 
# with a Postgres Checkpointer (e.g., PostgresSaver) to prevent database locks.
import os
db_path = "/tmp/chat_history.db" if os.environ.get("VERCEL") else "chat_history.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)
# Compile the graph WITH memory
app = graph.compile(checkpointer=memory)

# TODO: Inject lease analysis JSON into state when upload happens
def run_agent(message: str, thread_id: str = "default_thread"):
    # The config tells LangGraph which memory slot to read/write to
    config = {"configurable": {"thread_id": thread_id}}
    
    result = app.invoke({"messages": [("user", message)]}, config=config)
    return result["messages"][-1].content


# conda deactivate
# .\.venv\Scripts\Activate.ps1
