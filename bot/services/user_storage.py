import json
import os
from typing import Dict, Any, List
from ..config import Config
from datetime import datetime

FILE_PATH = Config.USER_FILE_PATH


def _ensure_file() -> None:
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)


def load_users() -> Dict[str, Any]:
    _ensure_file()
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
        except json.JSONDecodeError:
            return {}


def save_users(users: Dict[str, Any]) -> None:
    _ensure_file()
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def add_user(chat_id: int, username: str = None, first_name: str = None) -> None:
    users = load_users()
    key = str(chat_id)

    if key not in users:
        users[key] = {
            "username": username,
            "first_name": first_name,
            "group": None,
            "fan_mode": False,
        }
    else:
        if username and not users[key].get("username"):
            users[key]["username"] = username
        if first_name and not users[key].get("first_name"):
            users[key]["first_name"] = first_name
        users[key].setdefault("group", None)
        users[key].setdefault("fan_mode", False)

    save_users(users)


def update_user_group(chat_id: int, group: str) -> None:
    users = load_users()
    key = str(chat_id)

    if key not in users:
        users[key] = {
            "username": None,
            "first_name": None,
            "group": group,
            "fan_mode": False,
        }
    else:
        users[key]["group"] = group

    save_users(users)


# Fan mode
def set_fan_mode(chat_id: int, enabled: bool) -> None:
    users = load_users()
    key = str(chat_id)
    prof = users.get(key, {"username": None, "first_name": None, "group": None})
    prof["fan_mode"] = bool(enabled)
    users[key] = prof
    save_users(users)


def get_fan_mode(chat_id: int) -> bool:
    users = load_users()
    return bool(users.get(str(chat_id), {}).get("fan_mode", False))


def get_all_fan_enabled_chat_ids() -> List[int]:
    users = load_users()
    return [int(cid) for cid, prof in users.items() if prof.get("fan_mode")]

def set_fan_last_sent(chat_id: int):
    users = load_users()
    key = str(chat_id)
    prof = users.get(key)
    if prof:
        prof["fan_last_sent"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        users[key] = prof
        save_users(users)
