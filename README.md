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

```
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
pytest
```

## Build phases

1. **Foundation** (this commit) — FastAPI skeleton, config, DB session, health
   check, test scaffolding, CI.
2. **Netherlands calculation engine** — income tax, AOW/ANW/WLZ, employer cost,
   payroll cycle logic.
3. **Privacy-safe AI layer** — pseudonymization/exception service,
   gross-to-net validation, legislation Q&A (RAG, statute-only).
4. **Frontend** — dashboard, client management, import payroll, exception
   triage screen.
5. **Infrastructure** — containerization, deployment.
6. **Testing & compliance validation** — reconciliation against known-good
   calculations before anything touches real payroll data.
