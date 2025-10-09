import json
import os
from typing import Any

from config import Config

FILE_PATH = Config.USER_FILE_PATH


def load_users() -> dict[str, Any]:
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_users(users: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def add_user(chat_id: int, username: str = None, first_name: str = None) -> None:
    users = load_users()
    chat_id = str(chat_id)

    users.setdefault(chat_id, {"username": username, "first_name": first_name, "group": None})

    save_users(users)


def update_user_group(chat_id: int, group: str) -> None:
    users = load_users()
    chat_id = str(chat_id)

    if chat_id not in users:
        users[chat_id] = {"username": None, "first_name": None, "group": group}
    else:
        users[chat_id]["group"] = group

    save_users(users)
