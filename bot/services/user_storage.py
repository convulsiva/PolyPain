import json
import os

FILE_PATH = "storage/users.json"


def load_users():
    """Загружаем базу пользователей из JSON."""
    if not os.path.exists(FILE_PATH):
        return {"users": []}
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(data):
    """Сохраняем базу пользователей в JSON."""
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_user(chat_id: int, username: str = None, first_name: str = None):
    """Добавляем нового пользователя (если ещё нет в базе)."""
    data = load_users()
    users = data["users"]

    if not any(u["chat_id"] == chat_id for u in users):
        users.append({
            "chat_id": chat_id,
            "username": username,
            "first_name": first_name,
            "group": None
        })
        save_users(data)


def update_user_group(chat_id: int, group: str):
    """Обновляем группу пользователя или добавляем нового, если его ещё нет."""
    data = load_users()
    users = data["users"]

    for user in users:
        if user["chat_id"] == chat_id:
            user["group"] = group
            break
    else:
        # Если пользователя нет в базе, создаём нового
        users.append({
            "chat_id": chat_id,
            "username": None,
            "first_name": None,
            "group": group
        })

    save_users(data)
