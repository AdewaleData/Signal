# Signal

**Know what's happening now. Make safer decisions.**

Signal is a community signal verification and route assessment system. It helps someone like Amara, closing her shop in Aderin at 6:40 PM, answer one question:

> Is the road home safe enough to take right now?

This prototype does not provide guarantees of physical safety and is not a replacement for emergency services.

---

## 1. Problem

The problem is not a lack of information. In a tense moment, WhatsApp threads, neighbors, and radio chatter produce **too much noisy information** and **too little verified signal**.

By the time a reliable picture forms, it may already be too late to choose a route.

## 2. Product

Signal is **not** an incident-reporting social network.

Reporting is only one input. The product converts raw local signals into a transparent, time-sensitive assessment of a specific route:

`CLEAR` · `CAUTION` · `AVOID` · `UNKNOWN`

Every decision explains why it was reached.

## 3. Why this matters

Unverified rumors and delayed official updates leave people choosing between paralysis and guesswork. Signal is designed for the five-second decision: status first, then confidence, freshness, evidence, and action.

Absence of reports is **not** treated as safety. That state is **Not enough information**.

## 4. Core user journey

1. Open Signal.
2. Choose a destination.
3. See the current route assessment.
4. Understand whether the route is Clear, Caution, Avoid, or Unknown.
5. Open **Why this decision?** and inspect the evidence, including conflicts.
6. Submit a new report if something was observed.
7. Watch the assessment change when new independent evidence arrives.
8. Switch to an alternate route if needed.

Primary navigation: **Home · Routes · Reports · Profile**.

## 5. Architecture

```
frontend (Next.js, TypeScript, Tailwind, PWA)
        │
        ▼
backend (FastAPI)
        ├── api/          HTTP surface
        ├── services/     deterministic verification engine
        ├── models/       SQLAlchemy
        └── db/           PostgreSQL or SQLite + seed
```

The decision engine is a pure service. The API loads structured evidence and asks the engine for a result. An LLM, if present, never writes a safety state.

## 6. Decision engine

Implemented in `backend/app/services/`.

For reports on a route the engine:

1. Drops expired / stale-beyond-threshold incidents.
2. Keeps reports that match the route by place or proximity.
3. Clusters by location. Different roads are not grouped.
4. Scores the primary hazard cluster.
5. Applies a contradiction penalty when all-clear reports disagree.
6. Maps scores onto one of four states.

**UNKNOWN** — not enough recent, reliable evidence.  
**CAUTION** — a recent signal exists, but evidence is incomplete, single-source, or conflicting.  
**AVOID** — confidence ≥ 0.80, at least two independent recent sources, strong location agreement, incident still active, and contradiction is not dominating.  
**CLEAR** — sufficient positive all-clear evidence (official confirmation, or two independent recent all-clear reports) and no active hazard cluster.

`no reports` → `UNKNOWN`, never `CLEAR`.

## 7. Verification model

Prototype formula (not a scientifically validated safety model):

```
confidence =
    0.25 * source_reliability
  + 0.25 * corroboration
  + 0.20 * recency
  + 0.20 * location_agreement
  + 0.10 * evidence_quality
  - contradiction_penalty
```

Supporting rules:

- One person filing several reports still counts as **one** independent source.
- Recency decays on configurable bands: 0–10 min very fresh, 10–30 fresh, 30–60 aging, then stale, then expired.
- Relationships stored: `CORROBORATES`, `CONTRADICTS`, `UNRELATED`.

See `backend/app/services/confidence.py`.

## 8. AI role

Optional OpenAI-compatible API in `backend/app/services/ai_normalizer.py`.

AI may:

- normalize informal / pidgin text into structured fields
- extract incident type and location reference

AI must not:

- invent evidence, sources, or incidents
- output `SAFE` / `DANGEROUS` / `AVOID`

All model output is validated with Pydantic. If no API key is set, a rule-based normalizer is used. The app is fully usable without paid APIs.

## 9. Database

Tables: `users`, `reports`, `report_relationships`, `routes`, `route_segments`, `route_assessments`.

SQLAlchemy models live in `backend/app/models/`. Alembic migration: `backend/alembic/versions/001_initial.py`. On startup the API also creates tables and seeds the Aderin demo if the database is empty.

SQLite is the default for a laptop demo. PostgreSQL is supported via Docker Compose.

## 10. API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Liveness |
| GET | `/api/me` | Demo profile (Amara) |
| GET | `/api/routes` | Routes + live states |
| GET | `/api/routes/{id}` | Single route |
| GET | `/api/routes/{id}/assessment` | Route assessment |
| GET | `/api/routes/{id}/evidence` | Factors + reports |
| GET | `/api/reports` | Recent reports |
| GET | `/api/reports/{id}` | Single report |
| POST | `/api/reports` | Submit a report |
| POST | `/api/reports/normalize` | Normalize free text |
| POST | `/api/demo/simulate-report` | Add corroboration |
| POST | `/api/demo/confirm-report` | Add official confirmation |
| POST | `/api/demo/contradict-report` | Add a conflicting signal |
| POST | `/api/demo/reset` | Restore seeded demo |

## 11. Local setup

**Requirements:** Python 3.11+, Node 20+.

```bash
cp .env.example .env

# Backend
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (second terminal)
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Render

The repo includes `render.yaml`.

1. Push this project to GitHub.
2. In Render: **New** > **Blueprint**.
3. Select the repo. Render creates `signal-db`, `signal-api`, and `signal-web`.
4. Wait for the first deploy. The API seeds the Aderin demo on an empty database.
5. Open the `signal-web` URL.

If the web service builds before the API URL is known, trigger a manual **Clear build cache & deploy** on `signal-web`.

### Vercel (frontend)

Vercel hosts the Next.js app only. The API still needs Render or another host.

1. Import `AdewaleData/Signal`.
2. Set **Root Directory** to `frontend`.
3. Add env var `BACKEND_URL` = your API URL, for example `https://signal-api.onrender.com`.
4. Deploy.

Push `main` so Vercel picks up the MapLibre build fix.

Free web services sleep after idle time. The first request can take about a minute.

The browser talks to the Next.js app. Next.js proxies `/api` to `signal-api`, so you do not need a public CORS setup for the main demo.

### Docker

```bash
docker compose up --build
```

API: `http://localhost:8000` · App: `http://localhost:3000`

## 12. Environment variables

See `.env.example`. Important keys:

- `DATABASE_URL`: SQLite locally, Postgres on Render
- `CORS_ORIGINS`: extra frontend origins
- `FRONTEND_URL`: public web origin (set automatically on Render)
- `BACKEND_URL`: API origin used by the Next.js `/api` proxy
- `NEXT_PUBLIC_API_URL`: leave empty so the browser uses the proxy
- `OPENAI_API_KEY`: optional
- Freshness and avoid thresholds: optional overrides

Never commit real secrets.

## 13. Testing

```bash
cd backend
pytest -q
```

Coverage includes: no reports → unknown; one weak report → caution; independent corroboration raises confidence; strong corroboration → avoid; aging reports lose score; contradictions reduce confidence; no-evidence is not clear; same-source reports are not independent; different locations stay ungrouped; expired incidents are ignored.

## 14. Demo scenario

Town: **Aderin** (fictional). User: **Amara Okafor**, shop owner.

Seeded opening state, **Shop → Home** via Market Road:

- Status: **Use caution**
- Two independent recent reports near the pharmacy
- No official confirmation yet

On the route screen, **Demo controls**:

1. **Add corroboration** — a local responder confirms the blockage. Expect **Caution → Avoid**.
2. **Add contradiction** — a resident says the road appears clear. Confidence drops; state typically returns to **Caution**.
3. **Reset demo** — restore the opening story.

Other seeded routes:

- Station Road — Avoid
- River Road (alternate home route) — Clear
- Central Avenue — Clear
- Hill Road — Not enough information

## 15. Known limitations

- Demo identities and reliability scores are fictional.
- The scoring model is a prototype, not a validated risk model.
- Location matching uses a small Aderin gazetteer, not live GPS traces.
- The map is a schematic visualization, not a live tile provider.
- There is no real authentication, moderation, or abuse handling.
- Timestamps on seed reports are refreshed on startup so the story stays “a few minutes ago.”
- An LLM, if enabled, can mis-parse language; the engine still decides.

## 16. Future roadmap

- Historical reliability updates from confirmed outcomes
- Photo / audio evidence quality
- Offline-first PWA cache of the last assessment
- Multi-town gazetteers and real map tiles
- Trusted responder accounts with stronger verification
- Public SMS / radio ingest as additional raw signals

