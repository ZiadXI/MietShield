# Milestones

A phased plan to build MietShield without getting overwhelmed.

## Phase 1 — Foundation
- [ ] Set up project structure (backend + frontend folders)
- [ ] Get FastAPI running with a health check endpoint
- [ ] Connect to OpenRouter and verify LLM responds
- [ ] Create the German tenant law knowledge base (markdown)

## Phase 2 — LangGraph Core
- [ ] Define the AgentState
- [ ] Build the graph with all nodes
- [ ] Get the Q&A agent working end-to-end (question → answer with sources)
- [ ] Get the lease analyzer working end-to-end (text in → analysis out)

## Phase 3 — API Layer
- [ ] Wire `/api/chat` endpoint to the LangGraph graph
- [ ] Wire `/api/analyze-lease` with PDF upload + parsing
- [ ] Test both endpoints with curl / Postman

## Phase 4 — Frontend
- [ ] Build the chat interface
- [ ] Build the lease upload + results display
- [ ] Connect frontend to backend API
- [ ] Polish the UI (animations, responsive, dark theme)

## Phase 5 — Polish & Showcase
- [ ] Write the project README with screenshots
- [ ] Record a demo video / GIF
- [ ] Handle edge cases (empty input, bad PDF, API errors)
- [ ] Final testing
