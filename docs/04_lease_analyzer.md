# Lease Analyzer — Feature Specification

> **Purpose of this document:** This is your north star for building the Lease Analyzer.
> Read it fully before writing a single line of code. It tells you *what* to build and *why*.
> The *how* is your job — that's where the learning happens.

---

## 1. What Is This Feature?

The Lease Analyzer is the second core feature of MietShield. It allows a tenant to upload their lease contract (as a PDF), and receive a structured, clause-by-clause legal analysis showing which parts of the contract are legal, suspicious, or outright illegal under German law.

This is significantly more complex than the chat Q&A because:
- It accepts a **file upload**, not just a text message.
- It must produce a **structured output** (not just a paragraph of text).
- It needs to **cite specific laws** (e.g. §551 BGB).
- The output must be machine-readable JSON so the frontend can render nice UI cards.

---

## 2. What the User Experiences (User Story)

1. User opens MietShield and clicks **"Analyze My Lease"**.
2. They see a drag-and-drop upload zone and upload their PDF lease.
3. A loading spinner appears with a message like *"Reading your lease..."*
4. They receive a clean results page showing:
   - A list of extracted clauses (e.g. **Deposit**, **Notice Period**, **Minor Repairs**)
   - Each clause is colour-coded: 🟢 **Safe** / 🟡 **Review** / 🔴 **Red Flag**
   - A short explanation of why the clause is or isn't legal
   - The specific BGB law section that applies
5. At the bottom: a one-paragraph overall summary of the lease's health.

---

## 3. Functional Requirements

### 3.1 Input
- **Type:** PDF file upload via a `multipart/form-data` HTTP POST request.
- **Max size:** Reasonable limit (e.g. 10 MB) — a typical lease is under 1 MB.
- **Language of lease:** English or German. The AI should handle both.
- **Fallback:** If the PDF text cannot be extracted (e.g. scanned image), return a clear error message.

### 3.2 Processing Pipeline
The feature must:
1. **Accept** the uploaded PDF from the HTTP request.
2. **Extract** all readable text from the PDF.
3. **Pass** the extracted text to the AI analyzer.
4. **Return** a structured JSON response to the client.

### 3.3 Output — What the AI Must Analyse

The AI must look for and evaluate the following clause categories in the lease:

| Clause Topic | What to look for | Relevant German Law |
|---|---|---|
| **Security Deposit** | Amount requested. Legal max is 3 months' cold rent. | §551 BGB |
| **Notice Period** | How much notice does the tenant need to give? Legal minimum is 3 months. | §573c BGB |
| **Rent Increase** | Any rent increase clauses. Check if they're capped by law. | §558 BGB (Mietpreisbremse) |
| **Minor Repairs** | Is the tenant required to pay for minor repairs? Legal if capped at ~€100/repair, ~€300/year. | §535 BGB |
| **Cosmetic Repairs** | Is the tenant required to repaint or renovate at move-out? Blanket obligations are illegal. | §535 BGB |
| **Termination Rights** | Are both parties' termination rights correctly stated? | §573 BGB |
| **Subletting** | Is subletting explicitly forbidden? A blanket ban may be illegal. | §553 BGB |
| **Access Rights** | Can the landlord enter without notice? Illegal unless emergency. | §555a BGB |

> 🧠 **Note:** The AI should NOT only look for the above. It should also flag anything else in the lease that looks unusual or potentially problematic. The above are just the most common issues.

### 3.4 Output Schema — What the JSON Must Look Like

The API must return a JSON object that looks exactly like this:

```json
{
  "clauses": [
    {
      "topic": "Security Deposit",
      "extracted_text": "The tenant shall pay a deposit of 5 months' cold rent upon signing.",
      "risk_score": "Red Flag",
      "explanation": "German law (§551 BGB) caps the deposit at a maximum of 3 months' cold rent. A deposit of 5 months is illegal and you can refuse to pay more than 3 months.",
      "law_reference": "§551 BGB"
    },
    {
      "topic": "Notice Period",
      "extracted_text": "Either party may terminate with 3 months' written notice.",
      "risk_score": "Safe",
      "explanation": "The 3-month notice period meets the legal minimum under §573c BGB.",
      "law_reference": "§573c BGB"
    }
  ],
  "overall_summary": "This lease contains 1 critical illegal clause (deposit) and 1 item to review. We recommend addressing the deposit before signing."
}
```

**Risk score must be one of three values only:** `"Safe"`, `"Review"`, or `"Red Flag"`.

> 🧠 **Think about this:** How do you force an LLM to always output data in this exact format? What happens if it decides to reply with a paragraph instead? Research `.with_structured_output()` in LangChain.

---

## 4. API Contract

### Endpoint
```
POST /api/analyze-lease
Content-Type: multipart/form-data
```

### Request
- Field name: `file`
- Field type: PDF file

### Response — Success `200 OK`
```json
{
  "clauses": [ ... ],
  "overall_summary": "..."
}
```

### Response — Error `422 Unprocessable Entity`
```json
{
  "detail": "Could not extract text from the uploaded PDF. The file may be a scanned image."
}
```

> 🧠 **Think about this:** How does FastAPI handle file uploads? Look up `UploadFile` and `File` from `fastapi`. What's the difference between `request.body()` and how you read a file?

---

## 5. Architecture — Where Does Each Piece Go?

Here is the structure already set up for you. Your job is to fill in the empty files.

```
backend/
├── api/
│   ├── routes.py        ← Add the POST /api/analyze-lease endpoint here
│   └── schemas.py       ← Add ClauseAnalysis and LeaseAnalysisResponse Pydantic models here
├── agents/
│   └── nodes/
│       └── lease_analyzer.py  ← The LangChain chain that analyses the text goes here
└── utils/
    └── pdf_parser.py    ← The PDF text extraction function goes here
```

### Recommended Build Order
1. `schemas.py` — Define the data shapes first. Everything else depends on this.
2. `pdf_parser.py` — Write and test the PDF extraction in isolation.
3. `lease_analyzer.py` — Build the LangChain chain that takes text and returns a `LeaseAnalysisResponse`.
4. `routes.py` — Wire everything together in the endpoint last.

> 🧠 **Why this order?** Always design your data contracts (schemas) before writing logic. If you start coding without knowing the shape of your output, you'll refactor everything later. This is standard engineering practice.

---

## 6. Key Technical Decisions to Think About

Before you start coding, consider these. We can discuss them before you commit to an approach.

### Decision 1: How to force structured output from the LLM?
- **Option A:** Use LangChain's `.with_structured_output(LeaseAnalysisResponse)`. The LLM returns a Pydantic object directly.
- **Option B:** Write a detailed prompt asking for JSON output, then manually parse `json.loads(response.content)`.

> *What are the tradeoffs? What could go wrong with Option B? What happens if the model returns slightly malformed JSON?*

### Decision 2: What if the PDF is a scanned image (not text-based)?
- PyMuPDF extracts embedded text. Scanned PDFs have no embedded text — they're just images of pages.
- You could add OCR (Optical Character Recognition) with a library like `pytesseract`, but that's a significant added complexity.
- For the capstone, a clean error message is fine. Out of scope.

### Decision 3: What context does the LLM need?
- The AI needs to know German tenant law to evaluate clauses. Should you pass the entire `german_law.md` file into every prompt (simple but expensive/slow)?
- Or should you use RAG to retrieve only the relevant sections (more complex but smarter)?

> *For now, passing the full knowledge base in the prompt is acceptable. Note it as a future improvement.*

---

## 7. Things Left Empty for You to Think About

Before you discuss this with me, try to answer these on paper or in a comment block:

1. What is the Pydantic schema for a single `ClauseAnalysis`? What are its fields and types?
2. What is the Pydantic schema for the overall `LeaseAnalysisResponse`?
3. What does the system prompt to the LLM look like? What instructions does it need?
4. How do you read the file bytes from an `UploadFile` object in FastAPI?
5. How do you extract text page-by-page with PyMuPDF and join it into one string?

---

*When you feel you have answers to the above, come back and we'll discuss your thinking before you start writing code.*
