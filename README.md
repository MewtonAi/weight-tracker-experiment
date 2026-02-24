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
    main.py
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
uvicorn main:app --reload
```
Backend runs at: `http://127.0.0.1:8000`
API docs: `http://127.0.0.1:8000/docs`

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: `http://127.0.0.1:5173`

## Next planned enhancements (post-MVP)
- Goal weight + progress to goal
- Weekly/monthly summaries
- Export CSV
- Smoother mobile UX + responsive cards
- Optional auth + multi-user mode
