import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "weight_tracker.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
