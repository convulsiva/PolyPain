from typing import Optional, Union
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from functools import wraps
from config import Config

TObj = Union[Message, CallbackQuery]

def is_admin(user_id: Optional[int]) -> bool:
    return bool(user_id) and user_id in Config.ADMIN_IDS

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
