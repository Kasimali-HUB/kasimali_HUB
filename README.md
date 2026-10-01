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

## Running it (Codespaces or any local checkout)

```
./start-dev.sh
```

This is the one command to use. It installs both the backend and frontend
dependencies, starts the backend, **actually confirms it responds** before
doing anything else (not just that the command ran), then starts the
frontend. If the backend fails to come up, it prints the backend's own log
so the real error is visible immediately instead of a vague connection
failure somewhere downstream.

In Codespaces, `.devcontainer/devcontainer.json` sets both ports (8000 and
5173) to **public visibility automatically** the moment the container is
created or rebuilt - no manual Ports-tab clicking required, which was the
single biggest source of "it looks like it's running but nothing works"
confusion. If you already had a Codespace running before this file existed,
use "Rebuild Container" once (Command Palette → "Codespaces: Rebuild
Container") to pick it up.

When the frontend starts, open it from the **Ports tab's own link**, not a
previously saved browser tab - Codespaces can issue a new forwarded address
between sessions, and an old tab will 404 even though everything is working.

Press Ctrl+C in the terminal running `start-dev.sh` to stop both the
frontend and the backend together.

### Running backend and frontend separately (for development)

Backend only:
```
pip install -r requirements.txt
cp .env.example .env
python -m app.main
pytest
```
Dev mode uses a local SQLite file (created automatically on first run,
seeded with demo data) - nothing else needs to be installed or running.
Production overrides `DATABASE_URL` to a real Postgres instance.

`python -m app.main` (rather than `uvicorn app.main:app --reload`) matters
in Codespaces/Docker/WSL: it binds to `0.0.0.0` so the port can actually be
forwarded out of the container. `uvicorn`'s own default (`127.0.0.1`) only
accepts connections from inside the container - the port can still show as
"active" while being completely unreachable from your browser.

Frontend only:
```
cd frontend
npm install
cp .env.example .env
npm run dev
```
Runs at http://localhost:5173, calling the API at http://localhost:8000.
In Codespaces, the frontend detects its own forwarded address and finds
the backend's forwarded address automatically - no manual URL setup needed.

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
