# Milestones

A phased plan to build MietShield without getting overwhelmed.

## Phase 1 — Foundation
- [x] Set up project structure (backend + frontend folders)
- [x] Get FastAPI running with a health check endpoint
- [x] Connect to OpenRouter and verify LLM responds
- [x] Create the German tenant law knowledge base (markdown)

## Phase 2 — LangGraph Core
- [x] Define the AgentState (still not end-to-end)
- [x] Build the graph with all nodes (still not end-to-end)
- [x] Get the Q&A agent working end-to-end (question → answer with sources) (still not the full logic)
- [ ] Get the lease analyzer working end-to-end (text in → analysis out)

## Phase 3 — API Layer
- [x] Wire `/api/chat` endpoint to the LangGraph graph
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
