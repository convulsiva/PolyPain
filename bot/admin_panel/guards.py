from contextlib import suppress
from functools import wraps

from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from ..config import Config
from ..services import db_service

TObj = Message | CallbackQuery


def is_admin(user_id: int | None) -> bool:
    if not user_id:
        return False
    return user_id in Config.ADMIN_IDS or user_id in db_service.get_all_admins()


def _uid_from(obj: TObj) -> int | None:
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
                    with suppress(Exception):
                        if isinstance(obj, CallbackQuery):
                            bot.answer_callback_query(obj.id, text="⛔️ Нет доступа")
                        else:
                            bot.reply_to(obj, "⛔️ Нет доступа.")
                return None
            return func(obj, *args, **kwargs)

        return wrapper

    return decorator
