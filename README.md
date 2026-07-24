# AIVOA Complaint Management System - Round 1 Scaffold

## Demo Video\n[Watch the demo](https://drive.google.com/file/d/1VhU-43iC8qhbi7hRko2exGbj2gr-2dsY/view?usp=drive_link)

AI-powered customer complaint management system for the pharmaceutical
manufacturing industry (API/FDF quality complaints).

## Architecture

```
React + Redux (frontend)
        |
        v
FastAPI (backend/app/main.py)
        |
        v
LangGraph pipeline (backend/app/agents/graph.py)
  extract -> completeness_check -> risk_classification
          -> duplicate_check -> capa_recommendation -> summary
        |
        v
Groq API (gemma2-9b-it for extraction/summary,
          llama-3.3-70b-versatile for classification/reasoning)
        |
        v
Postgres/MySQL (backend/app/models.py)
```

### Why this LangGraph design
- **extract**: pulls structured fields from raw text using the required
  `gemma2-9b-it` model. Small/fast model, so the prompt is narrow and asks
  for JSON only.
- **completeness_check**: a plain Python node (no LLM call) that flags which
  of the required fields the extractor couldn't fill - this powers the
  "Complaint Completeness Checker" bonus feature and highlights missing
  fields in the form UI.
- **conditional edge**: if extraction confidence is very low, the graph
  skips straight to `summary` instead of letting downstream nodes reason
  over unreliable data - demonstrates LangGraph's conditional routing rather
  than a purely linear chain.
- **risk_classification / capa_recommendation**: use the larger
  `llama-3.3-70b-versatile` model since these require more reasoning.
- **duplicate_check**: compares against the last 50 saved complaints -
  covers the "Duplicate Complaint Detection" bonus.
- **summary**: short human-readable summary for a QA manager skimming a
  queue.

Chat ("Ask me anything about this complaint") is intentionally a separate,
lightweight call rather than a graph node, since each question is
independent and doesn't need multi-step orchestration.

## Setup

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY
# create the Postgres DB referenced in DATABASE_URL first
uvicorn app.main:app --reload
```
API runs at `http://localhost:8000`. Interactive docs at `/docs`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Runs at `http://localhost:5173`. Set `VITE_API_BASE` if the backend isn't
on `localhost:8000`.

### Testing the pipeline
Use `sample_data/sample_complaint_email.txt` - paste its contents into the
"Paste Complaint Text / Email" box, or `curl` it directly:
```bash
curl -X POST http://localhost:8000/api/complaints/extract \
  -H "Content-Type: application/json" \
  -d "{\"raw_text\": \"$(cat sample_data/sample_complaint_email.txt)\"}"
```

## What's stubbed vs. real
- Document parsing (PDF/DOCX/TXT) is functional but intentionally simple -
  no OCR, per the assignment's note that production-grade parsing isn't
  required.
- The chat assistant uses the raw complaint text as context directly
  rather than a vector store - fine at this scale (one complaint at a
  time), and keeps the assignment's LangGraph focus on the extraction
  pipeline rather than RAG infrastructure.
- CORS is wide open (`*`) for local development - tighten via
  `CORS_ORIGINS` before any real deployment.

## Next steps for a fuller submission
- Add a complaints list/dashboard view (the `GET /api/complaints` endpoint
  already exists for this).
- Add authentication if multi-user access is expected.
- Record the demo video walking through: file upload -> AI extraction ->
  form review -> save -> chat -> LangGraph flow in the code.
