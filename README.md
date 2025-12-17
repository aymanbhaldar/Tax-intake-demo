# 🧾 AI Tax Compliance Auditor

A production-grade, end-to-end **AI-powered tax document auditing system** designed to process real W-2 and 1099 forms safely, deterministically, and at scale.

This project demonstrates how to build **reliable AI systems** by combining large language models with traditional software engineering, instead of relying on probabilistic reasoning where correctness is critical.

---

## 🧠 Core Idea

Tax and compliance documents are not difficult to read.
They are difficult to **trust**.

Scanned PDFs, OCR noise, inconsistent formats, and numeric edge cases make naive “just use GPT” approaches unreliable in real-world compliance workflows.

This system is built around a simple principle:

> **Use AI for reading. Use deterministic code for reasoning.**

---

## ✅ What This System Does

* Accepts **batch uploads** of tax documents (PDF, PNG, JPG)
* Extracts structured data from W-2 and 1099 forms
* Performs a **30-point deterministic compliance audit**
* Flags risk conditions and OCR failures automatically
* Calculates confidence scores based on rule coverage
* Persists results to an auditable, reviewable data store

This is a working system built for real inputs, not a demo pipeline.

---

## 🚀 Key Features

### 📂 Batch Processing

* Multiple documents processed in a single run
* Each file handled independently with batch-safe execution
* No cross-file contamination or item collapse

### 🤖 Hybrid Intelligence Architecture

* **AI Layer (GPT-4o)**
  Used strictly for OCR and document classification
  No arithmetic, no validation, no decision-making

* **Logic Layer (JavaScript)**
  Performs all calculations, validations, thresholds, and inequality checks

### 🚨 Automated Risk Detection

* Flags abnormal withholding rates greater than 35% or less than 5%
* Detects OCR scan failures such as tax values exceeding wages
* Validates employee names using regex-based rules

### 📊 Deterministic Confidence Scoring

* Confidence derived from required field presence and validation rule coverage
* No model-generated confidence values

### 🔄 Session-Safe User Experience

* Upload, review, and reset flows are fully isolated
* Users can start new analyses without residual state

### 🧾 Persistent Audit Trail

* Results logged to Google Sheets
* Schema mirrors API output for transparency and traceability

---

## 🧩 System Architecture

High-level workflow:

1. User uploads documents via Streamlit frontend
2. Files are sent to an n8n webhook
3. Documents are split and processed individually
4. AI performs OCR and document classification
5. Deterministic JavaScript logic runs compliance checks
6. Results are aggregated and persisted
7. Frontend displays structured results with risk indicators

This architecture intentionally separates **reading** from **reasoning** to avoid AI hallucinations in high-stakes logic.

---

## 🛠️ Tech Stack

### 🎨 Frontend

* Streamlit (Python)
* Drag-and-drop batch uploader
* Session state management
* Expandable result views

### ⚙️ Backend Orchestration

* n8n
* Webhook-based API
* Batch-safe item processing
* Deterministic routing and aggregation

### 🤖 AI Layer

* GPT-4o
* Used only for OCR and document classification

### 🧠 Logic Core

* JavaScript
* Tax rate calculations
* Inequality checks
* Regex-based validation
* OCR error detection

### 🗂️ Persistence

* Google Sheets
* Append-only audit log
* Structured, human-readable records

### 🔗 Integration

* JSON-based API contract between frontend and backend
* Stateless request handling

---

## 🧪 Example Output

```json
{
  "document_type": "W-2",
  "confidence": 92,
  "effective_tax_rate": 0.032,
  "risk_flags": ["LOW_WITHHOLDING"],
  "status": "REVIEW_REQUIRED"
}
```

---

## 🧠 Engineering Highlights

* Built a full end-to-end system, not a single-file demo or notebook workflow
* Designed a hybrid AI architecture that separates document reading from reasoning
* Identified and mitigated LLM failure modes in numeric and logical tasks
* Moved all math, inequalities, and validation logic out of AI and into deterministic code
* Implemented batch-safe workflows without relying on fragile item indexing
* Solved nested JSON serialization issues across AI, orchestration, and UI layers
* Implemented rule-based confidence scoring instead of probabilistic estimates
* Designed the system to be auditable, traceable, and explainable by default

---



## ⚙️ Running the Project Locally

### Prerequisites

* Python 3.10+
* n8n (self-hosted or cloud)
* OpenAI API key

### Start the Frontend

```bash
streamlit run app.py
```

### Backend Setup

* Configure OpenAI credentials in n8n
* Copy the n8n webhook URL into the Streamlit app configuration

---

## 🚨 Known Limitations

* OCR accuracy depends on scan quality
* Currently supports W-2 and 1099 forms only
* Google Sheets is used for simplicity, not large-scale production workloads

---

## 🛣️ Roadmap

* Support for additional tax forms
* Database-backed persistence layer
* Role-based review workflows
* Jurisdiction-specific compliance rules

---

## 📜 License

This project is licensed under the **MIT License**.

The goal is to maximize learnability, reuse, and experimentation while keeping the system transparent and accessible.

---

## 🤝 Feedback

This project reflects how AI systems should be built in practice: models for flexible perception, deterministic code for correctness.

Feedback, discussions, and architectural critiques are welcome.
