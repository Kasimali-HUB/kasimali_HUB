# kasimali_HUB — GPIP (Global Payroll Intelligence Platform)

Global payroll platform, rebuilt from scratch. Starts with the Netherlands,
designed to add countries incrementally.

## Design principle: the AI/data boundary

Personal data (employee and client records) never crosses into any AI-assisted
component. The calculation engine is deterministic and stays fully within our
own systems. Anything AI touches is limited to:

- public legislation text (no personal data)
- pseudonymized IDs + numeric deltas (for exception triage — no names)
- template structures (filled with real data locally, after generation)

## Structure

```
app/
  core/       # settings
  db/         # SQLAlchemy session + base
  api/v1/     # versioned API routes
tests/
```

Import convention: always `from app...`, never `from backend.app...`.

## Local setup

Backend:
```
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
pytest
```
Dev mode uses a local SQLite file (created automatically on first run,
seeded with demo data) - nothing else needs to be installed or running.
Production overrides `DATABASE_URL` to a real Postgres instance.

Frontend:
```
cd frontend
npm install
cp .env.example .env
npm run dev
```
Runs at http://localhost:5173, calling the API at http://localhost:8000.

## Build phases

1. **Foundation** — FastAPI skeleton, config, DB session, health check,
   test scaffolding, CI.
2. **Netherlands calculation engine** — income tax, AOW/ANW/WLZ, employer
   cost, payroll cycle logic. Done, including AOW-age handling.
3. **Privacy-safe AI layer** — pseudonymization/exception service,
   gross-to-net validation. Done.
4. **Legislation Q&A** — RAG over a statute-only corpus, no employee data.
   Done.
5. **Frontend** — dashboard, client select, import payroll, exception
   review. Backend endpoints + React app done; real payroll-run ingestion
   (vs. demo data) still open.
6. **Infrastructure** — containerization, deployment.
7. **Testing & compliance validation** — reconciliation against known-good
   calculations before anything touches real payroll data.
