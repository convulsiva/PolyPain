from typing import Optional, Union
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from functools import wraps

from ..config import Config
from ..services import db_service

TObj = Union[Message, CallbackQuery]

def is_admin(user_id: Optional[int]) -> bool:
    if not user_id:
        return False
    return user_id in Config.ADMIN_IDS or user_id in db_service.get_all_admins()

def _uid_from(obj: TObj) -> Optional[int]:
    if isinstance(obj, CallbackQuery):
        return obj.from_user.id if obj and obj.from_user else None
    return obj.from_user.id if obj and obj.from_user else None

def admin_only(bot: TeleBot, reply_no_access: bool = True):
    def decorator(func):
        @wraps(func)
        def wrapper(obj: TObj, *args, **kwargs):
            uid = _uid_from(obj)
            if not is_admin(uid):
                if reply_no_access:
                    try:
                        if isinstance(obj, CallbackQuery):
                            bot.answer_callback_query(obj.id, text="⛔️ Нет доступа")
                        else:
                            bot.reply_to(obj, "⛔️ Нет доступа.")
                    except Exception:
                        pass
                return
            return func(obj, *args, **kwargs)
        return wrapper
    return decorator