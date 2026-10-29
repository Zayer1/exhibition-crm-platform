# Exhibition & Event CRM Platform

A high-performance B2B sales CRM, inventory constraint validation engine, and activity tracking backend built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**.

Designed to handle multi-stakeholder commercial workflows (Sales Directors, Account Managers, Technical Coordinators), finite fair/booth constraints, and automated handoff verification.

> **Project Context:** Originally developed as a **48-hour technical assessment challenge** for a B2B event technology firm. It was architected to demonstrate backend system design, relational database modeling, and deterministic business logic under a strict 48-hour delivery window.

---

## System Overview & Core Capabilities

- **Relational Data Integrity:** Normalized 6-table relational schema (`Company`, `Contact`, `Opportunity`, `FairEdition`, `ActivityLog`, `AgentRun`) modeling complex B2B event lifecycles.
- **Automated Handoff Assistant:** Integrated verification engine that deterministically audits opportunity requirements (stand area, requested height) against physical fair edition parameters before technical handoff.
- **Activity & Follow-Up Engine:** Chronological conversation tracking (calls, meetings, emails) with global scheduling dashboards to prevent dropped leads.
- **Idempotent Data Ingestion:** Automated startup ingestion pipeline capable of parsing multi-format European numerical and date structures without overwriting existing production records.

---

## Architectural Decisions & Engineering Rationale

### 1. 48-Hour Assessment Scope & Architectural Trade-offs
- **Core Priority:** Under the strict 48-hour constraint, engineering effort was concentrated entirely on rock-solid database integrity (foreign keys, normal forms), idempotent data ingestion, and business rule enforcement.
- **Conscious Omissions:** Enterprise authentication (JWT/RBAC) and complex frontend UI frameworks were intentionally kept minimal (vanilla HTML/JS) to focus available sprint hours on backend reliability and deterministic state machines.

### 2. Technology Stack
- **Backend:** Python 3, FastAPI, SQLAlchemy, Uvicorn
- **Database:** PostgreSQL (Relational schema with foreign key constraints)
- **Frontend Interface:** Lightweight HTML5 / CSS3 / JavaScript dashboard
- **API Architecture:** RESTful endpoints with structured Pydantic data contracts

### 3. Ingestion & Normalization
- **Relational Normalization:** Flat export files are ingested and decoupled into normalized entities to prevent duplicate contact records across different fair editions.
- **Idempotent Pipeline:** `app/importer.py` runs on server startup via FastAPI `lifespan` events. It parses all data files, handles European float formatting (`3,5` -> `3.5`) and Italian date formats, and safely skips re-importing if records already exist.

### 4. Engineering Note on AI & Deterministic Validation
In `app/agent.py`, a **deterministic rule engine** was intentionally selected over an LLM for opportunity constraint checking:
- Enforcing physical, numerical boundaries (e.g. `requested_area <= max_area` and `requested_height <= max_height`) requires **100% mathematical precision**.
- LLMs are subject to non-deterministic math hallucinations and introduce seconds of API latency and unnecessary cost. 
- *Architectural Principle:* Deterministic guardrails handle hard business rules; generative LLMs are best reserved for parsing unstructured conversational text or summarizing communications.

---

## Areas for Future Experimentation & Scaling

To transition this platform into a high-concurrency multi-tenant SaaS environment:

1. **Enterprise Concurrency & Multi-User Support:**
   - Implement optimistic locking on opportunity updates to prevent race conditions during simultaneous edits.
   - Introduce JWT-based authentication and Role-Based Access Control (RBAC).
   - Add database-level audit logs tracking modifications by user ID and timestamp.
2. **Hybrid AI Pipeline:**
   - Introduce an LLM extraction service to ingest unstructured client emails and automatically populate opportunity draft fields.
   - Pipe extracted parameters directly through the deterministic validation rules before committing to the database.
3. **Predictive Lead Scoring:**
   - Train a lightweight machine learning model (e.g., XGBoost or Random Forest) on historical closed-won opportunities to score close probabilities and prioritize sales outreach.
4. **Search Scalability:**
   - Implement PostgreSQL full-text search (`pg_trgm` / GiST indexes) or external Elasticsearch clustering to maintain sub-50ms search latency across 100,000+ contact and activity logs.

---

## Quickstart & Local Setup

### Option 1: Docker (Recommended)
```bash
# Start PostgreSQL and the CRM service
docker compose up -d

# Access the interface
open http://localhost:3000
```

### Option 2: Local Python Environment
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 3000
   ```
3. Open your browser:
   ```
   http://localhost:3000
   ```

---

## Verifying the Assistant Engine

1. Search for an exhibitor using prefix `C-` (e.g., `C-01`).
2. Open any Opportunity detail view.
3. **Valid Handoff:** Click **Run Assistant**. If the stand area and requested height fall within fair limits, the assistant approves the handoff and logs `PROCEED`.
4. **Constraint Violation Test:** Set "Requested Height" to an excessive value (e.g., `25`), save, and rerun the assistant. The engine flags the violation, outputs detailed failure diagnostics, and halts the handoff.
