
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# Store the database inside the backend folder.
BACKEND_DIR = Path(__file__).resolve().parent
DB_PATH = BACKEND_DIR / "chat_history.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    """Create the conversation and message tables."""

    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                message_type TEXT NOT NULL DEFAULT 'unverified',
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id)
                    REFERENCES conversations(session_id)
                    ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session
            ON messages(session_id, id)
        """)


def create_conversation(session_id):
    """Create a new conversation for an uploaded document session."""

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO conversations (session_id, created_at, updated_at)
            VALUES (?, ?, ?)
        """, (session_id, now, now))


def save_message(session_id, role, content, message_type="unverified"):
    """Save a user or assistant message."""

    if role not in ("user", "assistant"):
        raise ValueError("Invalid message role.")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Message content cannot be empty.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        result = conn.execute("""
            INSERT INTO messages
            (session_id, role, content, message_type, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, role, content, message_type, now))

        conn.execute("""
            UPDATE conversations
            SET updated_at = ?
            WHERE session_id = ?
        """, (now, session_id))

        return result.lastrowid


def get_chat_history(session_id):
    """Retrieve all messages belonging to a conversation."""

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT role, content, message_type, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
        """, (session_id,)).fetchall()

        return [dict(row) for row in rows]


def conversation_exists(session_id):
    """Check whether a conversation exists."""

    with get_connection() as conn:
        result = conn.execute("""
            SELECT 1 FROM conversations
            WHERE session_id = ?
        """, (session_id,)).fetchone()

        return result is not None
