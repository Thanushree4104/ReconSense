# ⚡ ReconSense

### AI-powered financial reconciliation & investigation for payment operations.

<p align="center">

**Detect. Investigate. Explain. Resolve.**

ReconSense goes beyond finding reconciliation mismatches —  
it investigates **why they happened**, shows the **evidence**,  
and recommends the **safest next action**.

</p>

---

## 🚨 The Problem

Payment operations deal with data scattered across:

**Payments → Settlements → Bank Transactions**

A mismatch is easy to detect.

**Finding out why it happened is not.**

Operations teams often have to manually:

🔍 Find related records  
💰 Compare amounts  
📄 Gather evidence  
🧠 Determine the likely cause  
✅ Decide what to do next  
📝 Record the investigation  

**ReconSense automates this investigation workflow.**

---

## 💡 What ReconSense Does

```text
        💳 PAYMENT
            │
            ▼
     🔄 RECONCILIATION
            │
            ▼
      🚨 EXCEPTION
            │
            ▼
     📎 EVIDENCE
            │
            ▼
      🧠 AI INVESTIGATION
            │
            ▼
   ┌─────────────────────┐
   │ Cause + Confidence   │
   │ Evidence + Action    │
   └──────────┬──────────┘
              │
              ▼
       🛡️ GOVERNANCE
              │
              ▼
        👤 HUMAN / ACTION
              │
              ▼
          📋 AUDIT
```

---

## 🎯 The Difference

| Traditional Recon | **ReconSense** |
|---|---|
| Finds mismatches | **Investigates mismatches** |
| Shows exception | **Explains likely cause** |
| Manual evidence gathering | **Evidence-backed investigation** |
| Analyst decides everything | **AI recommends bounded actions** |
| Limited traceability | **Governance + audit trail** |

> **ReconSense is not just a reconciliation engine.  
> It is an investigation layer on top of reconciliation.**

---

## 🧠 AI Investigation

For every exception, ReconSense produces:

| | |
|---|---|
| 🚨 **Exception** | What went wrong |
| 🔎 **Likely Cause** | Why it probably happened |
| 📊 **Confidence** | How confident the investigation is |
| 📎 **Evidence** | Records supporting the conclusion |
| 🎯 **Recommendation** | What should happen next |
| 🛡️ **Governance** | Whether the action is allowed |

### Example

**PAY_004 — Bank Mismatch**

```text
Payment Amount     ₹2,200.00
Settlement Net     ₹2,164.60
Bank Credit        ₹2,100.00
Difference         ₹64.60
```

**AI Investigation**

> The bank entry does not match the settlement amount, indicating a discrepancy that requires verification.

**Confidence:** `90%`

**Evidence:** `SET_004` · `BANK_004`

**Recommendation:** `Verify Bank Entry`

**Governance:** `Approval Required`

---

## 🛡️ AI With Guardrails

ReconSense does **not** give an AI model unrestricted control over financial operations.

```text
             🧠 AI Recommendation
                     │
                     ▼
              🛡️ Guardrails
                     │
                     ▼
             📜 Policy Engine
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       ✅ ALLOWED  ⚠️ APPROVAL  🚫 BLOCKED
```

AI recommendations are validated for:

- Evidence validity
- Confidence thresholds
- Supported actions
- Governance policies

---

## 🔄 AI Failure? No Problem.

The AI provider is **not a single point of failure**.

```text
             Investigation
                   │
                   ▼
              Groq AI 🤖
              /       \
          Success     Failure
             │          │
             ▼          ▼
          AI Result  Deterministic
                     Fallback
             \          /
              \        /
               ▼      ▼
              Guardrails
                   │
                   ▼
              Governance
                   │
                   ▼
                Audit
```

If the AI provider fails, ReconSense automatically falls back to a deterministic investigation provider.

**Both paths go through the same guardrails and governance layer.**

---

## 🔍 Supported Exceptions

| Exception | Meaning |
|---|---|
| 💰 `amount_mismatch` | Payment and settlement amounts differ |
| ⏳ `missing_settlement` | Settlement is missing or not settled |
| 🏦 `bank_mismatch` | Settlement and bank amounts differ |
| 🔁 `duplicate_settlement` | Duplicate settlement records detected |
| 🕐 `timing_difference` | Settlement and bank timing differs |
| 💸 `refund_difference` | Refund amounts do not reconcile |
| ❓ `unknown` | Exception cannot be confidently classified |

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────┐
│              PAYMENT DATA                   │
│      Payments • Settlements • Bank          │
└──────────────────────┬──────────────────────┘
                       ▼
              🔄 Reconciliation
                       │
                       ▼
              🚨 Exception Detection
                       │
                       ▼
                📎 Evidence Layer
                       │
                       ▼
              🧠 Investigation Agent
                  │          │
                  │          └── Deterministic Fallback
                  ▼
                Groq AI
                       │
                       ▼
                 🛡️ Guardrails
                       │
                       ▼
                📜 Governance
                       │
                       ▼
                  📋 Audit
```

---

## ⚙️ Tech Stack

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite)
![Groq](https://img.shields.io/badge/Groq-AI-orange)
![Pytest](https://img.shields.io/badge/Pytest-Testing-0A9EDC?logo=pytest)

</p>

---

## 🚀 Quick Start

### 1. Clone

```bash
git clone https://github.com/Thanushree4104/ReconSense.git
cd ReconSense
```

### 2. Install

```bash
uv sync
```

### 3. Configure

Create `.env`:

```env
GROQ_API_KEY=your_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

### 4. Run

```bash
uv run uvicorn app.api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

## 🔌 API

| Endpoint | Purpose |
|---|---|
| `GET /health` | System health |
| `GET /reconciliation` | Reconciliation results |
| `GET /investigations/{payment_id}` | AI investigation |
| `GET /investigations/{payment_id}/evidence` | Investigation evidence |
| `GET /investigations/{payment_id}/audit` | Audit trail |

---

## 🧪 Testing

```bash
uv run pytest
```

```bash
uv run ruff check .
```

```bash
uv run mypy backend
```

---

## 🔐 Design Principles

**Deterministic Truth**  
Financial reconciliation is rule-based, not LLM-based.

**Evidence Before Explanation**  
AI investigations are grounded in reconciliation evidence.

**Bounded AI**  
AI recommends actions — it does not independently authorize financial operations.

**Resilient by Design**  
AI failure triggers a deterministic fallback.

**Auditable**  
Investigation and governance events are recorded for traceability.

---

# ⚡ ReconSense

### **Don't just find the mismatch. Understand it.**