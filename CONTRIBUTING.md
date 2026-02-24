# CONTRIBUTING

Before opening a PR:

1. Apply migrations locally
   - `cd backend && alembic upgrade head`
2. Run backend tests
   - `cd backend && python -m pytest -q`
3. Run frontend tests
   - `cd frontend && npm test`
4. Run frontend build check
   - `cd frontend && npm run build`

Environment setup (optional but recommended):
- Copy `backend/.env.example` to `backend/.env`
- Copy `frontend/.env.example` to `frontend/.env`

Architecture expectations:
- Routes should not contain SQL.
- Business logic belongs in services.
- Persistence belongs in repositories.
- Keep API error responses in `{ code, message, details? }` shape.
- Keep schema changes migration-driven (no startup table mutation).
