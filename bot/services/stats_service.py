from collections import Counter
from typing import Any, Dict, List, Tuple
from .user_storage import load_users
from ..config import Config

def _normalize_users(raw: Any) -> Dict[str, Dict[str, Any]]:
    if isinstance(raw, dict) and "users" in raw and isinstance(raw["users"], list):
        out: Dict[str, Dict[str, Any]] = {}
        for u in raw["users"]:
            cid = u.get("chat_id")
            if cid is None:
                continue
            out[str(cid)] = {
                k: v for k, v in u.items() if k != "chat_id"
            }
        return out

    if isinstance(raw, dict):
        return {str(k): (v or {}) for k, v in raw.items()}

    return {}


def get_admin_stats() -> Dict[str, Any]:
    raw = load_users() or {}
    users_by_chat: Dict[str, Dict[str, Any]] = _normalize_users(raw)

    total_users = len(users_by_chat)
    unique_chats = total_users

    with_group = sum(
        1 for u in users_by_chat.values()
        if (u.get("group") or "").strip()
    )
    without_group = total_users - with_group

    groups: List[str] = [
        u["group"] for u in users_by_chat.values()
        if (u.get("group") or "").strip()
    ]
    group_top: List[Tuple[str, int]] = Counter(groups).most_common(5)

    return {
        "total_users": total_users,
        "unique_chats": unique_chats,
        "with_group": with_group,
        "without_group": without_group,
        "admins_count": len(Config.ADMIN_IDS),
        "admin_ids": sorted(Config.ADMIN_IDS),
        "group_top": group_top,
        "last_registered_at": None,
        "last_updated_at": None,
    }
