import re
from datetime import datetime, timedelta
from telebot import TeleBot, types
from telebot.types import Message

from .keyboards import build_fan_toggle_kb, main_menu
from .services import db_service
from .texts import (DAYS_RU, FAN_OFF_MSG, FAN_ON_MSG, FAN_STATUS_FMT,
                    GROUP_SAVED, HELP_MESSAGE, INVALID_GROUP_FORMAT, NO_GROUP,
                    NOT_REGISTERED, PING, SETGROUP_INSTRUCTION, START_MESSAGE,
                    UNKNOWN_COMMAND)


def register_handlers(bot: TeleBot):
    @bot.message_handler(commands=["start"])
    def start_handler(message: Message):
        db_service.add_or_update_user(
            chat_id=message.chat.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        bot.send_message(message.chat.id, START_MESSAGE, reply_markup=main_menu())

    @bot.message_handler(commands=["menu"])
    def menu_handler(message: Message):
        bot.send_message(message.chat.id, "Меню обновлено:", reply_markup=main_menu())


    def handle_daily_schedule(message: Message, day: str):
        user = db_service.get_user(message.chat.id)

        if not user or not user['group_name']:
            bot.reply_to(message, NO_GROUP)
            return

        group = user['group_name']
        text = ""
        if day == "today":
            text = get_today_text(group)
        elif day == "tomorrow":
            text = get_tomorrow_text(group)

        bot.reply_to(message, text, parse_mode="HTML")

    def get_today_text(group: str):
        today_eng = datetime.now().strftime("%A")
        today = DAYS_RU.get(today_eng, today_eng)
        return f"📅 Сегодня {today} для группы <b>{group}</b>\n\n09:00 — Математика\n10:40 — Физика"

    def get_tomorrow_text(group: str):
        tomorrow_eng = (datetime.now() + timedelta(days=1)).strftime("%A")
        tomorrow = DAYS_RU.get(tomorrow_eng, tomorrow_eng)
        return f"📅 Завтра {tomorrow} для группы <b>{group}</b>\n\n09:00 — Программирование\n10:40 — Английский"

    @bot.message_handler(commands=["today"])
    def today_command(message: Message):
        handle_daily_schedule(message, "today")

    @bot.message_handler(func=lambda msg: msg.text == "📅 Сегодня")
    def today_button(message: Message):
        handle_daily_schedule(message, "today")

    @bot.message_handler(commands=["tomorrow"])
    def tomorrow_command(message: Message):
        handle_daily_schedule(message, "tomorrow")

    @bot.message_handler(func=lambda msg: msg.text == "📆 Завтра")
    def tomorrow_button(message: Message):
        handle_daily_schedule(message, "tomorrow")

    def get_schedule_text(group: str):
        return (
            f"📅 Расписание для группы <b>{group}</b>\n\n"
            "<b>Понедельник:</b>\n09:00 — Математика\n10:40 — Физика\n\n"
            "<b>Вторник:</b>\n09:00 — Программирование\n10:40 — Английский\n\n"
            "<b>Среда:</b>\n09:00 — Химия\n10:40 — История\n"
        )

    def handle_schedule(message: Message):
        user = db_service.get_user(message.chat.id)
        if not user:
            bot.reply_to(message, NOT_REGISTERED)
            return
        if not user['group_name']:
            bot.reply_to(message, NO_GROUP)
            return
        bot.reply_to(message, get_schedule_text(user["group_name"]), parse_mode="HTML")

    @bot.message_handler(commands=["schedule"])
    def schedule_command(message: Message):
        handle_schedule(message)

    @bot.message_handler(func=lambda msg: msg.text == "🗓 Всё расписание")
    def schedule_button(message: Message):
        handle_schedule(message)

    # --- ПРОЧИЕ КОМАНДЫ ---

    @bot.message_handler(commands=["ping"])
    def ping_handler(message: Message):
        bot.reply_to(message, PING)

    @bot.message_handler(commands=["id"])
    def id_handler(message: Message):
        bot.reply_to(message, f"🆔 Твой chat_id: <code>{message.chat.id}</code>", parse_mode="HTML")

    @bot.message_handler(commands=["help"])
    def help_handler(message: Message):
        bot.reply_to(message, HELP_MESSAGE, parse_mode="HTML")

    @bot.message_handler(commands=["setgroup"])
    def setgroup_handler(message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, SETGROUP_INSTRUCTION, parse_mode="HTML")
            return
        group = parts[1].strip()
        if not re.fullmatch(r"\d+/\d+", group):
            bot.reply_to(message, INVALID_GROUP_FORMAT)
            return
        db_service.update_user_group(message.chat.id, group)
        bot.reply_to(message, GROUP_SAVED.format(group=group), parse_mode="HTML")


    @bot.message_handler(commands=["fan_on"])
    def fan_on_cmd(message: Message):
        db_service.set_fan_mode(message.chat.id, True)
        bot.reply_to(message, FAN_ON_MSG)

    @bot.message_handler(commands=["fan_off"])
    def fan_off_cmd(message: Message):
        db_service.set_fan_mode(message.chat.id, False)
        bot.reply_to(message, FAN_OFF_MSG)

    def _get_fan_status(chat_id: int) -> bool:
        user = db_service.get_user(chat_id)
        return user['fan_mode'] == 1 if user else False

    @bot.message_handler(commands=["fan"])
    def fan_status_cmd(message: Message):
        enabled = _get_fan_status(message.chat.id)
        status = "ВКЛ" if enabled else "ВЫКЛ"
        bot.send_message(
            message.chat.id, FAN_STATUS_FMT.format(status=status),
            parse_mode="HTML", reply_markup=build_fan_toggle_kb(enabled)
        )

    @bot.message_handler(func=lambda m: m.text == "🎉 Фан-режим")
    def fan_button(message: Message):
        enabled = _get_fan_status(message.chat.id)
        status = "ВКЛ" if enabled else "ВЫКЛ"
        bot.send_message(
            message.chat.id, FAN_STATUS_FMT.format(status=status),
            parse_mode="HTML", reply_markup=build_fan_toggle_kb(enabled)
        )

    @bot.callback_query_handler(func=lambda c: c.data in ("fan:on", "fan:off"))
    def fan_toggle(call: types.CallbackQuery):
        enabled = (call.data == "fan:on")
        db_service.set_fan_mode(call.from_user.id, enabled)
        new_status = "ВКЛ" if enabled else "ВЫКЛ"
        bot.answer_callback_query(call.id, text=("Включено" if enabled else "Выключено"))
        bot.edit_message_text(
            f"🎛 Статус фан-режима: <b>{new_status}</b>",
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            parse_mode="HTML", reply_markup=build_fan_toggle_kb(enabled)
        )

    # --- ОБЪЕДИНЕННЫЙ ОБРАБОТЧИК ДЛЯ ОСТАЛЬНЫХ СООБЩЕНИЙ ---
    @bot.message_handler(func=lambda msg: True)
    def fallback_and_easter_egg_handler(message: Message):
        text = message.text.lower()
        triggers = ["serega pirat", "серега пират", "пират"]
        if any(trigger in text for trigger in triggers):
            bot.send_sticker(
                message.chat.id,
                "CAACAgIAAxkBAAOcaMR5j0knrqDF0s1lONeOhEY2syYAAvsYAAIRSwhLT7Bhl6t0YIo2BA"
            )
        else:
            bot.reply_to(message, UNKNOWN_COMMAND)