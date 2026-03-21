import sqlite3
import json
from datetime import datetime
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_username TEXT UNIQUE NOT NULL,
            title TEXT,
            description TEXT,
            subscriber_count INTEGER,
            language TEXT,
            avg_post_views INTEGER,
            avg_reactions INTEGER,
            reaction_view_ratio REAL,
            post_frequency TEXT,
            admin_username TEXT,
            admin_contact TEXT,
            topics TEXT,
            tone TEXT,
            sample_posts TEXT,
            tgstat_url TEXT,
            source TEXT,
            relevance_notes TEXT,
            status TEXT DEFAULT 'discovered',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER REFERENCES channels(id),
            message_text TEXT NOT NULL,
            language TEXT NOT NULL,
            approved BOOLEAN DEFAULT FALSE,
            sent_at TIMESTAMP,
            response_received BOOLEAN DEFAULT FALSE,
            response_text TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS discovery_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            query_or_category TEXT,
            language TEXT,
            channels_found INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.close()


# --- Channel operations ---

def upsert_channel(username, source, **kwargs):
    """Insert or update a channel. Returns (channel_id, is_new)."""
    username = username.lstrip("@").lower()
    conn = get_connection()
    existing = conn.execute(
        "SELECT id, source FROM channels WHERE telegram_username = ?", (username,)
    ).fetchone()

    if existing:
        # Update source to include both if different
        old_source = existing["source"] or ""
        if source and source not in old_source:
            new_source = f"{old_source},{source}" if old_source else source
            kwargs["source"] = new_source
        if kwargs:
            sets = ", ".join(f"{k} = ?" for k in kwargs)
            vals = list(kwargs.values())
            vals.append(datetime.now().isoformat())
            vals.append(username)
            conn.execute(
                f"UPDATE channels SET {sets}, updated_at = ? WHERE telegram_username = ?",
                vals,
            )
            conn.commit()
        conn.close()
        return existing["id"], False

    conn.execute(
        "INSERT INTO channels (telegram_username, source) VALUES (?, ?)",
        (username, source),
    )
    if kwargs:
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values())
        vals.append(username)
        conn.execute(
            f"UPDATE channels SET {sets} WHERE telegram_username = ?", vals
        )
    conn.commit()
    channel_id = conn.execute(
        "SELECT id FROM channels WHERE telegram_username = ?", (username,)
    ).fetchone()["id"]
    conn.close()
    return channel_id, True


def update_channel(username, **kwargs):
    """Update channel fields."""
    username = username.lstrip("@").lower()
    conn = get_connection()
    kwargs["updated_at"] = datetime.now().isoformat()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [username]
    conn.execute(f"UPDATE channels SET {sets} WHERE telegram_username = ?", vals)
    conn.commit()
    conn.close()


def get_channel(username):
    """Get a single channel by username."""
    username = username.lstrip("@").lower()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM channels WHERE telegram_username = ?", (username,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_channel_by_id(channel_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM channels WHERE id = ?", (channel_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_channels(status=None, language=None, min_subscribers=None, order_by="created_at DESC"):
    """Get channels with optional filters."""
    conn = get_connection()
    query = "SELECT * FROM channels WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if language:
        query += " AND language = ?"
        params.append(language)
    if min_subscribers:
        query += " AND subscriber_count >= ?"
        params.append(min_subscribers)
    query += f" ORDER BY {order_by}"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_channels_ready_for_messages(language=None, min_subscribers=None):
    """Get scraped channels that don't have messages yet."""
    conn = get_connection()
    query = """
        SELECT c.* FROM channels c
        LEFT JOIN messages m ON c.id = m.channel_id
        WHERE c.status = 'scraped' AND m.id IS NULL
    """
    params = []
    if language:
        query += " AND c.language = ?"
        params.append(language)
    if min_subscribers:
        query += " AND c.subscriber_count >= ?"
        params.append(min_subscribers)
    query += " ORDER BY c.subscriber_count DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Message operations ---

def insert_message(channel_username, message_text, language):
    """Insert a message for a channel and update status."""
    channel = get_channel(channel_username)
    if not channel:
        raise ValueError(f"Channel @{channel_username.lstrip('@')} not found")
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (channel_id, message_text, language) VALUES (?, ?, ?)",
        (channel["id"], message_text, language),
    )
    conn.execute(
        "UPDATE channels SET status = 'message_ready', updated_at = ? WHERE id = ?",
        (datetime.now().isoformat(), channel["id"]),
    )
    conn.commit()
    conn.close()


def get_messages(channel_id=None):
    conn = get_connection()
    if channel_id:
        rows = conn.execute(
            "SELECT * FROM messages WHERE channel_id = ? ORDER BY created_at DESC",
            (channel_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM messages ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_sent(channel_username):
    """Mark a channel's message as sent."""
    channel = get_channel(channel_username)
    if not channel:
        raise ValueError(f"Channel @{channel_username.lstrip('@')} not found")
    conn = get_connection()
    conn.execute(
        "UPDATE messages SET sent_at = ? WHERE channel_id = ? AND sent_at IS NULL",
        (datetime.now().isoformat(), channel["id"]),
    )
    conn.execute(
        "UPDATE channels SET status = 'sent', updated_at = ? WHERE id = ?",
        (datetime.now().isoformat(), channel["id"]),
    )
    conn.commit()
    conn.close()


def record_response(channel_username, response_text):
    """Record a response from a channel admin."""
    channel = get_channel(channel_username)
    if not channel:
        raise ValueError(f"Channel @{channel_username.lstrip('@')} not found")
    conn = get_connection()
    conn.execute(
        "UPDATE messages SET response_received = TRUE, response_text = ? WHERE channel_id = ? AND sent_at IS NOT NULL",
        (response_text, channel["id"]),
    )
    conn.execute(
        "UPDATE channels SET status = 'responded', updated_at = ? WHERE id = ?",
        (datetime.now().isoformat(), channel["id"]),
    )
    conn.commit()
    conn.close()


def update_message_notes(message_id, notes):
    conn = get_connection()
    conn.execute("UPDATE messages SET notes = ? WHERE id = ?", (notes, message_id))
    conn.commit()
    conn.close()


def delete_message(message_id):
    """Delete a message and reset channel status to scraped."""
    conn = get_connection()
    msg = conn.execute("SELECT channel_id FROM messages WHERE id = ?", (message_id,)).fetchone()
    if msg:
        conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        remaining = conn.execute(
            "SELECT id FROM messages WHERE channel_id = ?", (msg["channel_id"],)
        ).fetchone()
        if not remaining:
            conn.execute(
                "UPDATE channels SET status = 'scraped', updated_at = ? WHERE id = ?",
                (datetime.now().isoformat(), msg["channel_id"]),
            )
    conn.commit()
    conn.close()


def approve_message(message_id):
    conn = get_connection()
    conn.execute("UPDATE messages SET approved = TRUE WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()


# --- Discovery run operations ---

def log_discovery_run(source, query_or_category, language, channels_found):
    conn = get_connection()
    conn.execute(
        "INSERT INTO discovery_runs (source, query_or_category, language, channels_found) VALUES (?, ?, ?, ?)",
        (source, query_or_category, language, channels_found),
    )
    conn.commit()
    conn.close()


def get_discovery_runs():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM discovery_runs ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Stats ---

def get_stats():
    conn = get_connection()
    stats = {}
    stats["total_channels"] = conn.execute("SELECT COUNT(*) as c FROM channels").fetchone()["c"]
    stats["by_status"] = {
        row["status"]: row["c"]
        for row in conn.execute("SELECT status, COUNT(*) as c FROM channels GROUP BY status").fetchall()
    }
    stats["by_language"] = {
        row["language"]: row["c"]
        for row in conn.execute(
            "SELECT language, COUNT(*) as c FROM channels WHERE language IS NOT NULL GROUP BY language ORDER BY c DESC"
        ).fetchall()
    }
    stats["total_messages"] = conn.execute("SELECT COUNT(*) as c FROM messages").fetchone()["c"]
    stats["messages_sent"] = conn.execute(
        "SELECT COUNT(*) as c FROM messages WHERE sent_at IS NOT NULL"
    ).fetchone()["c"]
    stats["responses_received"] = conn.execute(
        "SELECT COUNT(*) as c FROM messages WHERE response_received = TRUE"
    ).fetchone()["c"]
    stats["response_rate"] = (
        round(stats["responses_received"] / stats["messages_sent"] * 100, 1)
        if stats["messages_sent"] > 0
        else 0
    )
    conn.close()
    return stats


# Initialize DB on import
init_db()
