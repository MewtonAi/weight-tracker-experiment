from datetime import date
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = "weight_tracker.db"

app = FastAPI(title="Weight Tracker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS weight_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT NOT NULL,
            weight_kg REAL NOT NULL,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup_event():
    init_db()


class WeightEntryCreate(BaseModel):
    entry_date: date
    weight_kg: float = Field(..., ge=20, le=400)
    note: str | None = Field(default=None, max_length=280)


class WeightEntryUpdate(BaseModel):
    entry_date: date
    weight_kg: float = Field(..., ge=20, le=400)
    note: str | None = Field(default=None, max_length=280)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/entries")
def list_entries():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, entry_date, weight_kg, note FROM weight_entries ORDER BY entry_date DESC, id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/entries")
def create_entry(payload: WeightEntryCreate):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO weight_entries (entry_date, weight_kg, note) VALUES (?, ?, ?)",
        (payload.entry_date.isoformat(), payload.weight_kg, payload.note),
    )
    conn.commit()
    new_id = cur.lastrowid
    row = conn.execute(
        "SELECT id, entry_date, weight_kg, note FROM weight_entries WHERE id=?", (new_id,)
    ).fetchone()
    conn.close()
    return dict(row)


@app.put("/entries/{entry_id}")
def update_entry(entry_id: int, payload: WeightEntryUpdate):
    conn = get_conn()
    exists = conn.execute("SELECT id FROM weight_entries WHERE id=?", (entry_id,)).fetchone()
    if not exists:
        conn.close()
        raise HTTPException(status_code=404, detail="Entry not found")

    conn.execute(
        """
        UPDATE weight_entries
        SET entry_date=?, weight_kg=?, note=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
        """,
        (payload.entry_date.isoformat(), payload.weight_kg, payload.note, entry_id),
    )
    conn.commit()
    row = conn.execute(
        "SELECT id, entry_date, weight_kg, note FROM weight_entries WHERE id=?", (entry_id,)
    ).fetchone()
    conn.close()
    return dict(row)


@app.delete("/entries/{entry_id}")
def delete_entry(entry_id: int):
    conn = get_conn()
    cur = conn.execute("DELETE FROM weight_entries WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"ok": True}


@app.get("/stats")
def stats():
    conn = get_conn()
    rows = conn.execute(
        "SELECT entry_date, weight_kg FROM weight_entries ORDER BY entry_date ASC, id ASC"
    ).fetchall()
    conn.close()

    if not rows:
        return {
            "current_weight": None,
            "entries_count": 0,
            "change_last_7": None,
            "avg_last_7": None,
        }

    data = [dict(r) for r in rows]
    current_weight = data[-1]["weight_kg"]

    last_7 = data[-7:]
    avg_last_7 = round(sum(x["weight_kg"] for x in last_7) / len(last_7), 2)
    change_last_7 = None
    if len(last_7) >= 2:
        change_last_7 = round(last_7[-1]["weight_kg"] - last_7[0]["weight_kg"], 2)

    return {
        "current_weight": current_weight,
        "entries_count": len(data),
        "change_last_7": change_last_7,
        "avg_last_7": avg_last_7,
    }
