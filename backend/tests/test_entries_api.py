import sqlite3
from pathlib import Path

import pytest
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS goal_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            goal_weight_kg REAL NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    db.DB_PATH = str(tmp_path / "test.db")
    _reset_schema(Path(db.DB_PATH))
    return TestClient(app)


def _create_entry(client: TestClient, *, entry_date: str, weight_kg: float, note: str | None = None):
    response = client.post("/entries", json={"entry_date": entry_date, "weight_kg": weight_kg, "note": note})
    assert response.status_code == 200
    return response


def test_duplicate_day_returns_409(client: TestClient):
    payload = {"entry_date": "2026-02-20", "weight_kg": 80.5, "note": "a"}
    r1 = client.post("/entries", json=payload)
    assert r1.status_code == 200

    r2 = client.post("/entries", json=payload)
    assert r2.status_code == 409
    body = r2.json()
    assert body["code"] == "ENTRY_DATE_EXISTS"


@pytest.mark.parametrize(
    "seeded,expected",
    [
        ([], {"current_weight": None, "entries_count": 0, "change_last_7": None, "avg_last_7": None}),
        (
            [("2026-02-20", 80.0)],
            {"current_weight": 80.0, "entries_count": 1, "change_last_7": None, "avg_last_7": 80.0},
        ),
        (
            [("2026-02-20", 80.0), ("2026-02-21", 79.5)],
            {"current_weight": 79.5, "entries_count": 2, "change_last_7": -0.5, "avg_last_7": 79.75},
        ),
        (
            [
                ("2026-02-20", 81.0),
                ("2026-02-21", 80.7),
                ("2026-02-22", 80.4),
                ("2026-02-23", 80.2),
                ("2026-02-24", 80.0),
                ("2026-02-25", 79.8),
                ("2026-02-26", 79.6),
                ("2026-02-27", 79.4),
            ],
            # Uses the last 7 entries (2026-02-21..2026-02-27)
            {"current_weight": 79.4, "entries_count": 8, "change_last_7": -1.3, "avg_last_7": 80.01},
        ),
    ],
)
def test_stats_matrix(client: TestClient, seeded: list[tuple[str, float]], expected: dict):
    for entry_date, weight_kg in seeded:
        _create_entry(client, entry_date=entry_date, weight_kg=weight_kg)

    response = client.get("/stats")
    assert response.status_code == 200
    assert response.json() == expected


def test_update_conflict_when_changing_date_to_existing(client: TestClient):
    first = _create_entry(client, entry_date="2026-02-20", weight_kg=81.0).json()
    _create_entry(client, entry_date="2026-02-21", weight_kg=80.5)

    response = client.put(
        f"/entries/{first['id']}",
        json={"entry_date": "2026-02-21", "weight_kg": 80.9, "note": "moved"},
    )

    assert response.status_code == 409
    body = response.json()
    assert body["code"] == "ENTRY_DATE_EXISTS"


def test_not_found_error_shape_consistent_for_delete_and_update(client: TestClient):
    delete_response = client.delete("/entries/999")
    update_response = client.put(
        "/entries/999",
        json={"entry_date": "2026-02-20", "weight_kg": 80.0, "note": None},
    )

    assert delete_response.status_code == 404
    assert update_response.status_code == 404

    delete_body = delete_response.json()
    update_body = update_response.json()

    assert delete_body["code"] == "ENTRY_NOT_FOUND"
    assert update_body["code"] == "ENTRY_NOT_FOUND"
    assert delete_body["message"] == update_body["message"]


def test_validation_error_shape(client: TestClient):
    r = client.post("/entries", json={"entry_date": "bad-date", "weight_kg": 10})
    assert r.status_code == 422
    body = r.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert isinstance(body.get("details"), list)


def test_goal_roundtrip(client: TestClient):
    create = client.post("/entries", json={"entry_date": "2026-02-21", "weight_kg": 88.0, "note": None})
    assert create.status_code == 200

    update_goal = client.put("/goal", json={"goal_weight_kg": 80})
    assert update_goal.status_code == 200
    body = update_goal.json()
    assert body["goal_weight_kg"] == 80
    assert body["current_weight"] == 88.0
    assert body["remaining_kg"] == 8.0


def test_csv_export_returns_rows(client: TestClient):
    client.post("/entries", json={"entry_date": "2026-02-20", "weight_kg": 81.2, "note": "Morning"})
    response = client.get("/entries/export.csv")

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "date,weight_kg,note" in response.text
    assert "2026-02-20,81.2,Morning" in response.text
