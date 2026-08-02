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


from typing import Annotated
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List,add_messages]
    user_info: str
    lease_text: str


@tool
def search_law(state:AgentState):
    """Call this tool to search the German Tenancy Law database for rules and regulations."""
    # Ensure correct path to your knowledge file
    file_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "german_law.md")
    with open(file_path, "r", encoding="utf-8") as file:
        law_text = file.read()
    return law_text   

tools = [search_law]
llm = ChatOpenAI(
    openai_api_key=os.getenv("openai_api_key"),
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="openrouter/free"

).bind_tools(tools)

def model_call(state:AgentState)->AgentState:
      system_prompt = SystemMessage(content="You are a strict German Tenant Law AI. ALWAYS use the search_law tool before answering.")
      response = llm.invoke([system_prompt]+state["messages"])
      return {"messages":response}
    
    
graph = StateGraph(AgentState)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.add_node("model_call",model_call)
graph.add_edge(START,"model_call")

graph.add_conditional_edges("model_call", tools_condition)

graph.add_edge("tools", "model_call")


app = graph.compile()

def run_agent(message: str):
    result = app.invoke({"messages": [("user", message)]})
    return result["messages"][-1].content


print(run_agent("Homeowner told me he wants deposit equals to 5 month pay"))

# conda deactivate
# .\.venv\Scripts\Activate.ps1
