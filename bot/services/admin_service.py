import json
import os
from typing import List, Set

ADMIN_FILE_PATH = "storage/admins.json"

def _ensure_file():
    os.makedirs(os.path.dirname(ADMIN_FILE_PATH), exist_ok=True)
    if not os.path.exists(ADMIN_FILE_PATH):
        with open(ADMIN_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_admins() -> Set[int]:
    _ensure_file()
    with open(ADMIN_FILE_PATH, "r", encoding="utf-8") as f:
        try:
            return set(json.load(f))
        except json.JSONDecodeError:
            return set()

def save_admins(admin_ids: Set[int]) -> None:
    _ensure_file()
    with open(ADMIN_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(list(admin_ids), f, indent=2)

def add_admin(user_id: int) -> bool:
    admins = load_admins()
    if user_id in admins:
        return False
    admins.add(user_id)
    save_admins(admins)
    return True

def remove_admin(user_id: int) -> bool:
    admins = load_admins()
    if user_id not in admins:
        return False
    admins.remove(user_id)
    save_admins(admins)
    return True