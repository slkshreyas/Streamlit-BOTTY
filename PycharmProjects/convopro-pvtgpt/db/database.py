# db/database.py
import sqlite3
from config.settings import Settings

settings = Settings()
DB_PATH = settings.SQLITE_DB_PATH


def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist yet."""
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id              TEXT PRIMARY KEY,
            title           TEXT NOT NULL,
            last_interacted TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            conv_id   TEXT    NOT NULL,
            role      TEXT    NOT NULL,
            content   TEXT    NOT NULL,
            ts        TEXT    NOT NULL,
            FOREIGN KEY (conv_id) REFERENCES conversations(id)
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_last_interacted
        ON conversations(last_interacted DESC)
    """)

    conn.commit()
    conn.close()


# Auto-run on import
init_db()