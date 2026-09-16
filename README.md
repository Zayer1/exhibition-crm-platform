# Exhibition sales CRM

Read [the assignment](ASSIGNMENT.md) first.

Create your own public Git repository for the work. If you received this starter as a ZIP, initialise Git in the extracted project and commit the starter before making changes. Submit by email using the required format in [What to send us](ASSIGNMENT.md#what-to-send-us).

The starter runs PostgreSQL. Add your application services to `compose.yml` and put your code wherever suits your stack. The export is in `data/`; its [README](data/README.md) describes the files and field formats.

Run `./dev.sh` to start and `docker compose down` to stop. `./reset.sh` removes the project's data. Once you've added the application, `./verify.sh` checks that it responds on port 3000. Until then, the HTTP check will fail.

## Submission notes

### Stack and Versions
- **Backend:** Python 3, FastAPI, SQLAlchemy, Uvicorn
- **Database:** PostgreSQL (Relational structure)
- **Frontend:** Vanilla HTML5, CSS3, JavaScript
- **API Architecture:** RESTful endpoints

### Time Spent
Completed rapidly over a single comprehensive session.

### Import Decisions
- **Data Normalization:** The original flat CSV exports were parsed and relationally normalized into a PostgreSQL database with 6 tables (`Company`, `Contact`, `Opportunity`, `FairEdition`, `ActivityLog`, and `AgentRun`).
- **Idempotent Import:** The `app/importer.py` script automatically runs on server startup via FastAPI `lifespan` events. It parses all four data files, handles European float formatting and Italian date formats, and safely skips import if data already exists to preserve user changes.

### Handling the Team's Requests
- **Reviewing & Modifying Hand-overs:** Included editable fields for Opportunity Budget, Stand Area, Requested Height, and Status.
- **Activity & Follow-up Tracking:** Added a streamlined UI to log conversations (calls, meetings, emails) directly to an opportunity and schedule follow-ups. A global "Follow-ups" dashboard displays all upcoming tasks chronologically.
- **Handoff Assistant:** Integrated a simulated AI agent (`app/agent.py`) that deterministically evaluates the opportunity constraints against the Fair limitations. It outputs `PROCEED` or `STOP/FAIL` with detailed reasoning, permanently logging its runs to the database.
  - *Engineering Note on AI:* A deterministic model was chosen over an LLM for constraint checking because enforcing hard rules (e.g., `requested_area > max_area`) requires 100% accuracy. LLMs can hallucinate math and take seconds to resolve, whereas this rules-engine approach is instantaneous, free, and perfectly reliable. AI is best reserved for parsing unstructured data rather than strictly evaluating numerical thresholds.

### Areas for Future Experimentation & Scaling
If this CRM were to scale into a production environment, here is what I would want to experiment with next:
- **Enterprise Data Integrity & Multi-User Support:**
  - Implement robust concurrency controls (e.g., optimistic locking) to prevent users from silently overwriting each other's edits.
  - Introduce user authentication and role-based access control.
  - Add comprehensive audit trails to tie every data modification to a specific user and timestamp.
- **Hybrid AI Architecture:**
  - Introduce an LLM (like GPT-4) purely for parsing unstructured data (e.g., extracting budgets from client emails).
  - Pipe the LLM's parsed outputs directly into the existing deterministic guardrails for reliable mathematical validation.
- **Predictive ML (Lead Scoring):**
  - Train a lightweight traditional Machine Learning model (e.g., Random Forest) on historical closed-won opportunities.
  - Generate a "Probability to Close" score to help the sales team prioritize follow-ups.
- **Search Scalability:**
  - To support the goal of 100,000+ contacts with heavy text logging, basic PostgreSQL indexing will eventually bottleneck.
  - I plan to dedicate time to researching and benchmarking full-text search strategies (e.g., Elasticsearch or pg_trgm) before proposing a definitive architecture.

### Running the Application (Local Testing)
1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `uvicorn app.main:app --reload`
3. Access the UI: http://localhost:3000

### Testing the Assistant
1. Search for a company using the prefix `C-` (e.g., `C-01`).
2. Click on any Opportunity to view details.
3. **Complete Enquiry:** Click **Run Assistant**. If the requested height and stand area are within the limits of the Fair Edition, it will approve the handoff.
4. **Incomplete/Failed Enquiry:** Edit the "Requested Height" to be a massive number (e.g., `25`), save it, and run the assistant again. The agent will flag the violation and block the handoff.
