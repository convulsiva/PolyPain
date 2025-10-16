from collections import Counter
from typing import Any, Dict, List, Tuple

from . import db_service


def get_admin_stats() -> Dict[str, Any]:
    users = db_service.get_all_users_for_stats()

    total_users = len(users)

    with_group = sum(1 for u in users if u['group_name'])

    groups: List[str] = [u['group_name'] for u in users if u['group_name']]
    group_top: List[Tuple[str, int]] = Counter(groups).most_common(5)

    return {
        "total_users": total_users,
        "unique_chats": total_users,
        "with_group": with_group,
        "without_group": total_users - with_group,
        "group_top": group_top,
    }