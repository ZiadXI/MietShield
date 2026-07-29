# Functional Requirements

## Problem

International students renting in Germany often don't know their legal rights. Landlords may include illegal clauses, overcharge deposits, or violate privacy — and tenants don't push back because they don't know they can.

## Target User

International tenants in Germany, primarily students.

## Core Features

### 1. Tenant Rights Q&A (Chat)
- User asks a question in plain English
- AI answers based on German rental law (BGB §535–580a)
- Response cites specific legal sections
- Conversational — follows up on previous messages

### 2. Lease Analyzer (Upload)
- User uploads a lease (PDF or pasted text)
- AI extracts key clauses and checks them against the law
- Each clause gets a risk score: 🟢 OK / 🟡 Review / 🔴 Red Flag
- Returns a summary with actionable recommendations

---

## User Stories

- *"As a student, I want to ask if my landlord can enter my apartment without notice, so I know my privacy rights."*
- *"As a tenant, I want to upload my lease and find out if my deposit amount is legal."*

---

## Non-Functional Requirements

<!-- 
🧠 YOUR TURN: Think about these and fill in what matters to you.
    Some prompts to consider:
    - Does the app need to be fast? What's acceptable response time?
    - Does it need to work offline?
    - How important is accuracy vs speed?
    - Any privacy concerns with uploading leases to an AI?
-->

- **Response time**: ___
- **Privacy**: ___
- **Accuracy**: ___
- **Other**: ___

---

## Out of Scope (for now)

- Multilingual support (German UI) — English only for capstone
- Lawyer matching / legal referrals
- User accounts / saved conversations
- Mobile app
