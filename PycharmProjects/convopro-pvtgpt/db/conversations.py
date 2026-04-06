# db/conversations.py
# All database operations for conversations and messages using SQLite

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from db.database import get_connection


# ── helpers ──────────────────────────────────────────────────────────────────

def now_utc() -> str:
    """Returns current UTC time as ISO string for storing in SQLite."""
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    """Generates a unique conversation ID."""
    return str(uuid.uuid4())


# ── core functions ────────────────────────────────────────────────────────────

def create_new_conversation(
    title: Optional[str] = None,
    role: Optional[str] = None,
    content: Optional[str] = None
) -> str:
    """
    Creates a new conversation in the DB.
    Optionally adds the first message right away.
    Returns the new conversation ID.
    """
    conv_id = new_id()
    ts = now_utc()

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO conversations (id, title, last_interacted) VALUES (?, ?, ?)",
            (conv_id, title or "Untitled Conversation", ts)
        )
        if role and content:
            conn.execute(
                "INSERT INTO messages (conv_id, role, content, ts) VALUES (?, ?, ?, ?)",
                (conv_id, role, content, ts)
            )
        conn.commit()
    finally:
        conn.close()

    return conv_id


def add_message(conv_id: str, role: str, content: str) -> bool:
    """
    Adds a single message to an existing conversation.
    Also updates last_interacted timestamp.
    Returns True on success.
    """
    ts = now_utc()

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO messages (conv_id, role, content, ts) VALUES (?, ?, ?, ?)",
            (conv_id, role, content, ts)
        )
        conn.execute(
            "UPDATE conversations SET last_interacted = ? WHERE id = ?",
            (ts, conv_id)
        )
        conn.commit()
    finally:
        conn.close()

    return True


def get_conversation(conv_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches a full conversation with all its messages.
    Returns a dict like: { "_id", "title", "messages": [{role, content}] }
    Returns None if not found.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM conversations WHERE id = ?", (conv_id,)
        ).fetchone()

        if not row:
            return None

        msgs = conn.execute(
            "SELECT role, content FROM messages WHERE conv_id = ? ORDER BY ts ASC",
            (conv_id,)
        ).fetchall()

    finally:
        conn.close()

    return {
        "_id": row["id"],
        "title": row["title"],
        "messages": [{"role": m["role"], "content": m["content"]} for m in msgs]
    }


def get_all_conversations() -> Dict[str, str]:
    """
    Returns all conversations sorted by most recent first.
    Returns dict: { conv_id: title }
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, title FROM conversations ORDER BY last_interacted DESC"
        ).fetchall()
    finally:
        conn.close()

    return {row["id"]: row["title"] for row in rows}
