from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from .services import admin_service

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
        InlineKeyboardButton("✉️ Написать пользователю", callback_data="admin:dm"),
    )
    kb.add(
        InlineKeyboardButton("👥 Список админов", callback_data="admin:list"),
    )
    kb.add(
        InlineKeyboardButton("➕ Добавить админа", callback_data="admin:add"),
        InlineKeyboardButton("➖ Удалить админа", callback_data="admin:remove_by_id")
    )
    return kb
