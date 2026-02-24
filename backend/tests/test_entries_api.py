import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

import app.db as db
from app.main import app


def _reset_schema(db_file: Path) -> None:
    conn = sqlite3.connect(db_file)
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
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_weight_entries_entry_date ON weight_entries(entry_date)")
    conn.commit()
    conn.close()


def test_duplicate_day_returns_409(tmp_path: Path):
    db.DB_PATH = str(tmp_path / "test.db")
    _reset_schema(Path(db.DB_PATH))
    client = TestClient(app)

    payload = {"entry_date": "2026-02-20", "weight_kg": 80.5, "note": "a"}
    r1 = client.post("/entries", json=payload)
    assert r1.status_code == 200

    r2 = client.post("/entries", json=payload)
    assert r2.status_code == 409
    body = r2.json()
    assert body["code"] == "ENTRY_DATE_EXISTS"


def test_not_found_error_shape_on_delete(tmp_path: Path):
    db.DB_PATH = str(tmp_path / "test.db")
    _reset_schema(Path(db.DB_PATH))
    client = TestClient(app)

    r = client.delete("/entries/999")
    assert r.status_code == 404
    assert r.json()["code"] == "ENTRY_NOT_FOUND"


def test_validation_error_shape(tmp_path: Path):
    db.DB_PATH = str(tmp_path / "test.db")
    _reset_schema(Path(db.DB_PATH))
    client = TestClient(app)

    r = client.post("/entries", json={"entry_date": "bad-date", "weight_kg": 10})
    assert r.status_code == 422
    body = r.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert isinstance(body.get("details"), list)
