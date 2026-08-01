import os
from typing import Dict, TypedDict,List
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: List[HumanMessage]
# llm = ChatOpenAI(model="gpt-4o")
llm = ChatOpenAI(
    openai_api_key=os.getenv("openai_api_key"),
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="openrouter/free"

)

def process(state: AgentState)-> AgentState:
    res = llm.invoke(state["messages"])
    print(f"AI: {res.content}")
    return state

graph = StateGraph(AgentState)
graph.add_node("process",process)
graph.add_edge(START,"process")
graph.add_edge("process",END)
agent = graph.compile()

user_input = ""
while user_input != "exit":
 user_input = input("Enter: ")
 agent.invoke({"messages":[HumanMessage(content=user_input)]})

 