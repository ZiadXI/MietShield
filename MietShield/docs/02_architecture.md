# Architecture

## High-Level Overview

```
User (Browser) → Frontend (HTML/JS) → FastAPI Backend → LangGraph Agent(s) → OpenRouter (LLM)
```

The frontend is a static site. The backend is a Python API that runs the AI pipeline.

---

## Backend

**Framework**: FastAPI — async, lightweight, great for AI backends.

**LLM Access**: OpenRouter — single API to access many open-source models. Uses `langchain-openrouter` package.

**Knowledge Base**: A curated markdown file of German tenant law, chunked and indexed with FAISS for retrieval (RAG). No external database needed.

**PDF Parsing**: PyMuPDF — extracts text from uploaded lease PDFs.

---

## The LangGraph Graph

This is the core of the project. A `StateGraph` that orchestrates the AI agents.

<!-- 
🧠 YOUR TURN: This is the most important design decision in the project.
   Sketch this out on paper before writing code. Think about:

   1. What NODES do you need? (A node = a step that does one thing)
      - Hint: you need at least something to decide what the user wants,
        something to answer questions, and something to analyze leases.

   2. What EDGES connect them? (How does one node lead to another?)
      - Hint: not every message goes to every agent.

   3. What STATE do they share? (What info needs to flow between nodes?)
      - Hint: think about what the lease analyzer needs that the Q&A agent doesn't.

   4. Are there any LOOPS? (Does any node need to retry or validate itself?)
      - Hint: what if the analysis output is bad? should it just return garbage?

   Draw your graph here (text diagram, mermaid, or just describe the flow):
-->

### Nodes

> TODO: Define your nodes here.

### Edges & Flow

> TODO: Define how nodes connect.

### State Shape

> TODO: What data flows through the graph?

---

## Frontend

A single-page-style app with two views:

1. **Chat view** — message input, scrollable conversation, source citations
2. **Analyzer view** — file upload zone, results displayed as cards with risk badges

The frontend talks to the backend via `fetch()` to two endpoints:
- `POST /api/chat` — send a message, get a response
- `POST /api/analyze-lease` — upload a file, get analysis results

---

## Key Libraries

| Library | Purpose |
|---|---|
| `langgraph` | Agent orchestration (StateGraph) |
| `langchain-openrouter` | LLM access via OpenRouter |
| `langchain-core` | Base message types, prompts |
| `faiss-cpu` | Vector similarity search for RAG |
| `fastapi` | API server |
| `pymupdf` | PDF text extraction |
| `python-dotenv` | Environment variable management |
