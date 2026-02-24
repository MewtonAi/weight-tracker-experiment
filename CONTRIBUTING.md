# CONTRIBUTING

Before opening a PR:

1. Apply migrations locally
   - `cd backend && alembic upgrade head`
2. Run backend tests
   - `cd backend && pytest -q`
3. Run frontend build check
   - `cd frontend && npm run build`

Architecture expectations:
- Routes should not contain SQL.
- Business logic belongs in services.
- Persistence belongs in repositories.
- Keep API error responses in `{ code, message, details? }` shape.
