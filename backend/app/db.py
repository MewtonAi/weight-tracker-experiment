import sqlite3

DB_PATH = "weight_tracker.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Temporary safety net for local runs; migrations are source of truth."""
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
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_weight_entries_entry_date ON weight_entries(entry_date)"
    )
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
