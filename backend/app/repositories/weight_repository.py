import sqlite3

from app.db import get_conn


class WeightRepository:
    def list_entries(self) -> list[dict]:
        conn = get_conn()
        rows = conn.execute(
            "SELECT id, entry_date, weight_kg, note FROM weight_entries ORDER BY entry_date DESC, id DESC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def create_entry(self, *, entry_date: str, weight_kg: float, note: str | None) -> dict:
        conn = get_conn()
        try:
            cur = conn.execute(
                "INSERT INTO weight_entries (entry_date, weight_kg, note) VALUES (?, ?, ?)",
                (entry_date, weight_kg, note),
            )
            conn.commit()
            new_id = cur.lastrowid
            row = conn.execute(
                "SELECT id, entry_date, weight_kg, note FROM weight_entries WHERE id=?", (new_id,)
            ).fetchone()
            return dict(row)
        finally:
            conn.close()

    def get_entry_by_id(self, entry_id: int) -> dict | None:
        conn = get_conn()
        row = conn.execute(
            "SELECT id, entry_date, weight_kg, note FROM weight_entries WHERE id=?", (entry_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def update_entry(self, *, entry_id: int, entry_date: str, weight_kg: float, note: str | None) -> dict:
        conn = get_conn()
        try:
            conn.execute(
                """
                UPDATE weight_entries
                SET entry_date=?, weight_kg=?, note=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
                """,
                (entry_date, weight_kg, note, entry_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT id, entry_date, weight_kg, note FROM weight_entries WHERE id=?", (entry_id,)
            ).fetchone()
            return dict(row)
        finally:
            conn.close()

    def delete_entry(self, entry_id: int) -> bool:
        conn = get_conn()
        try:
            cur = conn.execute("DELETE FROM weight_entries WHERE id=?", (entry_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    def list_entries_asc(self) -> list[dict]:
        conn = get_conn()
        rows = conn.execute(
            "SELECT entry_date, weight_kg FROM weight_entries ORDER BY entry_date ASC, id ASC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def list_entries_for_export(self) -> list[dict]:
        conn = get_conn()
        rows = conn.execute(
            "SELECT entry_date, weight_kg, note FROM weight_entries ORDER BY entry_date DESC, id DESC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_goal_weight(self) -> float | None:
        conn = get_conn()
        row = conn.execute("SELECT goal_weight_kg FROM goal_settings WHERE id=1").fetchone()
        conn.close()
        return float(row["goal_weight_kg"]) if row and row["goal_weight_kg"] is not None else None

    def upsert_goal_weight(self, goal_weight_kg: float) -> float:
        conn = get_conn()
        try:
            conn.execute(
                """
                INSERT INTO goal_settings (id, goal_weight_kg, updated_at)
                VALUES (1, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    goal_weight_kg=excluded.goal_weight_kg,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (goal_weight_kg,),
            )
            conn.commit()
            row = conn.execute("SELECT goal_weight_kg FROM goal_settings WHERE id=1").fetchone()
            return float(row["goal_weight_kg"])
        finally:
            conn.close()

    def is_unique_violation(self, exc: sqlite3.IntegrityError) -> bool:
        return "weight_entries.entry_date" in str(exc) or "UNIQUE constraint failed" in str(exc)
