from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("📅 Сегодня"), KeyboardButton("📆 Завтра"))
    markup.row(KeyboardButton("🗓 Всё расписание"))
    markup.row(KeyboardButton("🎉 Фан-режим"))
    return markup


def build_fan_toggle_kb(enabled: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    if enabled:
        kb.add(InlineKeyboardButton("🔕 Выключить", callback_data="fan:off"))
    else:
        kb.add(InlineKeyboardButton("🔔 Включить", callback_data="fan:on"))
    return kb


def build_admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Статистика", callback_data="admin:stats"),
        InlineKeyboardButton("📢 Рассылка", callback_data="admin:broadcast"),  # <-- НОВАЯ КНОПКА
    )
    kb.add(
        InlineKeyboardButton("👥 Список админов", callback_data="admin:list"),
        InlineKeyboardButton("✉️ Написать юзеру", callback_data="admin:dm"),
    )
    kb.add(
        InlineKeyboardButton("➕ Добавить админа", callback_data="admin:add"),
        InlineKeyboardButton("➖ Удалить по ID", callback_data="admin:remove_by_id"),
    )
    return kb
