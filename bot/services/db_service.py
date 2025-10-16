import sqlite3
import json
from typing import Optional, List, Set, Dict, Any
from datetime import datetime

from ..config import Config


def get_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                group_name TEXT,
                fan_mode INTEGER NOT NULL DEFAULT 0,
                fan_daily_sent TEXT NOT NULL DEFAULT '{}'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY
            )
        """)
        conn.commit()


# --- Функции для работы с пользователями (замена user_storage.py) ---

def add_or_update_user(chat_id: int, username: str, first_name: str):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO users (chat_id, username, first_name) VALUES (?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
        """, (chat_id, username, first_name))
        conn.commit()


def update_user_group(chat_id: int, group_name: str):
    with get_connection() as conn:
        conn.execute("UPDATE users SET group_name = ? WHERE chat_id = ?", (group_name, chat_id))
        conn.commit()


def get_user(chat_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
        return cursor.fetchone()


def set_fan_mode(chat_id: int, enabled: bool):
    with get_connection() as conn:
        conn.execute("UPDATE users SET fan_mode = ? WHERE chat_id = ?", (1 if enabled else 0, chat_id))
        conn.commit()


def get_all_fan_enabled_chat_ids() -> List[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM users WHERE fan_mode = 1")
        return [row[0] for row in cursor.fetchall()]


def increment_fan_daily_sent(chat_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fan_daily_sent FROM users WHERE chat_id = ?", (chat_id,))
        result = cursor.fetchone()
        if not result:
            return

        counters_json = result[0]
        counters = json.loads(counters_json)

        day_key = datetime.now().strftime("%Y-%m-%d")
        counters[day_key] = counters.get(day_key, 0) + 1

        if len(counters) > 7:
            for k in sorted(counters.keys())[:-7]:
                counters.pop(k, None)

        new_counters_json = json.dumps(counters)
        conn.execute("UPDATE users SET fan_daily_sent = ? WHERE chat_id = ?", (new_counters_json, chat_id))
        conn.commit()


def add_admin(user_id: int) -> bool:
    with get_connection() as conn:
        try:
            conn.execute("INSERT INTO admins (user_id) VALUES (?)", (user_id,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def remove_admin(user_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_all_admins() -> Set[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM admins")
        return {row[0] for row in cursor.fetchall()}


def get_all_users_for_stats() -> List[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id, group_name FROM users")
        return cursor.fetchall()