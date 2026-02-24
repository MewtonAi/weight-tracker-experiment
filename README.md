# weight-tracker-experiment

A web app MVP for tracking body weight over time.

## Tech stack
- **Backend:** Python + FastAPI + SQLite + Alembic
- **Frontend:** React + Vite + Mantine UI + Recharts

## Features
- Daily weight logging (date, weight, optional note)
- One entry per date (conflict-safe)
- History table with edit/delete
- Trend chart + basic stats
- Goal weight with progress metrics
- CSV export for entries
- Light/Dark mode toggle

## Project structure
```
weight-tracker-experiment/
  backend/
    main.py                      # compatibility entrypoint, exports app from app.main
    app/
      api/                       # transport layer (routes + error mapping)
      services/                  # business rules
      repositories/              # sqlite persistence
      models/                    # request/response schemas
    alembic/
      versions/                  # migration files
    tests/
  frontend/
    src/
      App.jsx
```

## Run guide

### 1) Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

Backend runs at: `http://127.0.0.1:8000`
API docs: `http://127.0.0.1:8000/docs`

### Migration commands
```bash
cd backend
alembic upgrade head          # apply all migrations
alembic downgrade -1          # rollback one revision
alembic revision -m "msg"     # create new migration file
```

### Backend tests
```bash
cd backend
pytest -q
```

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://127.0.0.1:5173`

### Frontend tests
```bash
cd frontend
npm test
```

## API error contract
All non-2xx API responses follow:
```json
{
  "code": "STRING_CODE",
  "message": "Human readable message",
  "details": {}
}
```

Current standardized codes:
- `VALIDATION_ERROR` (422)
- `ENTRY_NOT_FOUND` (404)
- `ENTRY_DATE_EXISTS` (409)
- `INTERNAL_SERVER_ERROR` (500)

## Engineering guardrails
- Keep domain rules in the service layer.
- Keep routes transport-only.
- Run migrations and tests before committing.
- Add/adjust tests with core-flow bug fixes.
