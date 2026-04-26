# Safety Operations API

FastAPI backend for the CFO AI POC. Exposes the LangGraph agent and Postgres
data layer as REST + Server-Sent Events.

## Quick start

```bash
# From repo root
source venv/bin/activate
docker compose start                # ensures finance-postgres is up
uvicorn api.main:app --reload --port 8000
```

Open http://localhost:8000/docs for interactive API docs.

## Prerequisites

- finance-postgres container running (see project root docker-compose.yml)
- Users table seeded: `python -m api.scripts.init_auth`
- `.env` populated with POSTGRES_*, JWT_*, and API_CORS_ORIGINS

## Default accounts

| Username | Password   | Role   |
|----------|------------|--------|
| admin    | admin123   | admin  |
| cfo      | demo123    | viewer |

**Change these before any non-local deployment.**

## Endpoints

### Auth
- `POST /auth/register` — create a new user
- `POST /auth/login` — returns JWT access token (form-encoded username/password)
- `GET  /auth/me` — current user (requires Bearer token)

### Dashboard (JWT required)
- `GET /dashboard/kpis?year=2022`
- `GET /dashboard/trend?months=24`
- `GET /dashboard/states?year=2022&top_n=10`
- `GET /dashboard/weather?year=2022&min_incidents=500&top_n=10`
- `GET /dashboard/hotspots?year=2022&top_n=15`
- `GET /dashboard/years`

### Chat (JWT required)
- `POST /chat/stream` — Server-Sent Events; body: `{ question, history: [...] }`

Event sequence: `thinking → narrative → chart → followups → cost → done`.

## Directory map


## Common workflows

### Get a token manually

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "$TOKEN"
```

### Call a protected endpoint

```bash
curl http://localhost:8000/dashboard/kpis?year=2022 \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

### Stream the chat endpoint

```bash
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"Top 5 states by severe accidents in 2022","history":[]}'
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `password authentication failed` | `.env` POSTGRES_PASSWORD doesn't match container | Check `docker inspect finance-postgres` env |
| `Could not validate credentials` (401) | Token expired (default 60 min) or missing | Re-login |
| `connection refused on port 5433` | finance-postgres not running | `docker compose start` |
| `email-validator not installed` | Pydantic EmailStr dependency missing | `pip install email-validator` |
| `Not authenticated` on /dashboard | Forgot to click Authorize in Swagger | 🔒 → login → Close |

## Running alongside Streamlit

Streamlit (`streamlit run ui/exec_app.py`) runs on **8501**.
FastAPI runs on **8000**.
They share the same Postgres and the same `agent/` code.

Both can run at once — use two terminals.

