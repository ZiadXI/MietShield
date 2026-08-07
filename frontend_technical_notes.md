# MietShield Frontend — Technical Notes for the Developer

> Things worth knowing. Skip the CSS pixels, keep the architecture.

---

## 1. Session Identity: `crypto.randomUUID()`

When you click **"New Chat"**, the frontend runs this one line:
```js
const newId = crypto.randomUUID();
// Example output: "a3f2c1e0-88b3-4d21-b9f7-c1a0e2d3f4b5"
```

**`crypto.randomUUID()`** is a built-in Web API — no external library needed, no backend call needed. It generates a cryptographically random UUID (Universally Unique Identifier) right in the browser.

This UUID becomes the `thread_id` sent to your FastAPI backend on every `/chat` request. LangGraph uses it as the key to look up the correct memory folder in `chat_history.db`. **This is how the frontend and backend memory stay in sync without a login system.**

---

## 2. Memory Lives in Two Places (by design)

| Where | What | Why |
|---|---|---|
| `localStorage` (Browser) | Chat messages, session labels, list of thread IDs | So the sidebar survives page refresh without a server call |
| `chat_history.db` (SQLite on Server) | The LangGraph message history used by the LLM | So the AI remembers past messages when answering new questions |

**Important nuance:** The browser's `localStorage` and LangGraph's database are **separate**. If you clear your browser's localStorage, the sidebar chat list disappears — but LangGraph's database still has the history. If you type the same `thread_id` again, the AI will still remember everything.

---

## 3. Why We Never Use `innerHTML` for User Data (XSS)

You will notice this function in `app.js`:
```js
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;   // 'textContent' treats the string as plain text
  return div.innerHTML;    // Returns the HTML-encoded version
}
```

This is called **XSS (Cross-Site Scripting) prevention**. If an AI response contained something like `<script>stealYourCookies()</script>`, and we blindly inserted it into the DOM with `innerHTML`, the browser would execute that script!

By routing all user-generated and AI-generated content through `escapeHtml()`, we ensure that `<` becomes `&lt;` and `>` becomes `&gt;`, making it harmless plain text. This is a **fundamental frontend security practice**.

---

## 4. The `thread_id` Contract (Frontend ↔ Backend)

The chat flow works like a relay race:

```
Browser generates UUID → saves to localStorage
       ↓
User types a message → Browser sends { message, thread_id } to /api/chat
       ↓
FastAPI receives it → calls run_agent(message, thread_id=thread_id)
       ↓
LangGraph looks up thread_id in SQLite → finds past messages → adds new message → invokes LLM
       ↓
LLM sees FULL conversation history → gives a contextually-aware response
       ↓
FastAPI returns { response: "..." } → Browser appends to chat window & saves to localStorage
```

Without `thread_id`, every single message would be a fresh conversation with zero memory.

---

## 5. CORS — Why It Exists (What's Already Done)

CORS (Cross-Origin Resource Sharing) is a browser security mechanism that blocks JavaScript running on `file:///your-local-html` from talking to a server at `http://127.0.0.1:8000`. Without it, every `fetch()` call would be rejected by the browser with a CORS error.

Your `main.py` already has this handled:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allows any origin (fine for local dev/portfolio)
    allow_methods=["*"],   # Allows GET, POST, etc.
    allow_headers=["*"],
)
```

> [!WARNING]
> `allow_origins=["*"]` means ANY website can call your API. For a portfolio project running locally this is fine. In a real production app, you would replace `"*"` with your actual frontend domain, e.g., `["https://mietshield.com"]`, to prevent other sites from abusing your API.

---

## 6. FormData vs JSON — When to Use Which

The upload endpoint sends a PDF file, so it uses **`FormData`**:
```js
const formData = new FormData();
formData.append("file", file);
fetch("/api/upload-lease", { method: "POST", body: formData });
// No "Content-Type" header needed — the browser sets it automatically with the boundary
```

The chat endpoint sends simple text, so it uses **JSON**:
```js
fetch("/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: text, thread_id: currentThreadId })
});
```

**Rule of thumb:** Files → `FormData`. Structured data → `JSON`.

---

## 7. The `LeaseAnalyzerResponse` Shape (Your Clean JSON Contract)

Your backend returns perfectly structured data:
```json
{
  "clauses": [
    {
      "topic": "Security Deposit",
      "extracted_text": "...",
      "risk_score": "Red Flag",
      "explanation": "...",
      "law_reference": "§ 551 BGB"
    }
  ],
  "overall_summary": "..."
}
```

The frontend reads `data.clauses` and loops over it to dynamically build the UI. **This is exactly what you designed with Pydantic.** The clean, typed JSON from your backend made building the frontend trivial. This is the real-world benefit of thinking in schemas first.

---

## 8. What's Still Not Wired Up (Honest Status)

| Feature | Status | Notes |
|---|---|---|
| UUID session → backend memory | ✅ Done | Frontend generates UUID, sends it, LangGraph stores it |
| Lease analysis dashboard | ✅ Done | Reads `clauses[]` array, renders cards with risk badges |
| Chat persistence (browser) | ✅ Done | Saved to `localStorage` |
| Chat persistence (LangGraph) | ✅ Done | Saved to `chat_history.db` via `SqliteSaver` |
| Lease context in chat | ⚠️ Partially | The AI doesn't automatically receive the lease JSON in the chat. The user has to ask a question and the AI's memory only has the chat history, not the lease JSON itself. |
| RAG / Vector DB for law search | ❌ Not built yet | Currently reads a flat `.md` file. |

> [!NOTE]
> The biggest architectural gap is **#5 above**: when a user uploads a lease, the JSON analysis is shown in the dashboard, but the Chat Agent in `state.py` doesn't automatically receive that JSON. If the user asks "Why is my deposit flagged?", the AI won't know unless the user tells it. Fixing this is the next major backend task: inject the `LeaseAnalyzerResponse` into the LangGraph state when the upload happens.

---

*You designed the backend like a professional. Clean schemas, separated concerns, persistent memory. The frontend just consumed your clean API.*
