# weight-tracker-experiment

A web app MVP for tracking body weight over time.

## Tech stack
- **Backend:** Python + FastAPI + SQLite
- **Frontend:** React + Vite + Mantine UI + Recharts

## MVP scope
- Daily weight logging (date, weight, optional note)
- History table with edit/delete
- Trend chart
- Basic stats (current, entries count, 7-day avg, 7-day delta)
- Light/Dark mode toggle
- Input validation

## Project structure
```
weight-tracker-experiment/
  backend/
    main.py                      # compatibility entrypoint, exports app from app.main
    app/
      api/                       # route and error handling layer
      services/                  # domain/business logic
      repositories/              # sqlite persistence layer
      models/                    # request/response schemas
    alembic/
      versions/                  # migration files
    alembic.ini
    requirements.txt
  frontend/
    package.json
    src/
      App.jsx
      main.jsx
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

# Run migrations
alembic upgrade head

# Start API
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

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: `http://127.0.0.1:5173`

## API error contract
All non-2xx API responses now follow:
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

## Next planned enhancements (post-MVP)
- Goal weight + progress to goal
- Weekly/monthly summaries
- Export CSV
- Smoother mobile UX + responsive cards
- Optional auth + multi-user mode
