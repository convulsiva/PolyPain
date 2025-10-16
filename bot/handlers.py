from telebot import TeleBot, types
from telebot.types import Message
from datetime import datetime, timedelta
from .texts import FAN_ON_MSG, FAN_OFF_MSG, FAN_STATUS_FMT
from .keyboards import main_menu, build_fan_toggle_kb
from .services.user_storage import add_user, update_user_group, load_users, set_fan_mode, get_fan_mode
from .texts import START_MESSAGE, HELP_MESSAGE, INVALID_GROUP_FORMAT, GROUP_SAVED, NOT_REGISTERED, NO_GROUP, PING, DAYS_RU, UNKNOWN_COMMAND, SETGROUP_INSTRUCTION
import re

def register_handlers(bot: TeleBot):
    @bot.message_handler(commands=["start"])
    def start_handler(message: Message):
        add_user(
            chat_id=message.chat.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        bot.send_message(message.chat.id, START_MESSAGE, reply_markup=main_menu())

    @bot.message_handler(commands=["menu"])
    def menu_handler(message: Message):
        bot.send_message(message.chat.id, "Меню обновлено:", reply_markup=main_menu())

    # TODAY
    def get_today_text():
        today_eng = datetime.now().strftime("%A")
        today = DAYS_RU.get(today_eng, today_eng)
        return f"📅 Сегодня {today}\n09:00 — Математика\n10:40 — Физика"

    @bot.message_handler(commands=["today"])
    def today_command(message: Message):
        bot.reply_to(message, get_today_text())

    @bot.message_handler(func=lambda msg: msg.text == "📅 Сегодня")
    def today_button(message: Message):
        bot.reply_to(message, get_today_text())

    # TOMORROW
    def get_tomorrow_text():
        tomorrow_eng = (datetime.now() + timedelta(days=1)).strftime("%A")
        tomorrow = DAYS_RU.get(tomorrow_eng, tomorrow_eng)
        return f"📅 Завтра {tomorrow}\n09:00 — Программирование\n10:40 — Английский"

    @bot.message_handler(commands=["tomorrow"])
    def tomorrow_command(message: Message):
        bot.reply_to(message, get_tomorrow_text())

    @bot.message_handler(func=lambda msg: msg.text == "📆 Завтра")
    def tomorrow_button(message: Message):
        bot.reply_to(message, get_tomorrow_text())

    # ===== SCHEDULE =====
    def get_schedule_text(group: str):
        return (
            f"📅 Расписание для группы {group}\n\n"
            "Понедельник:\n09:00 — Математика\n10:40 — Физика\n\n"
            "Вторник:\n09:00 — Программирование\n10:40 — Английский\n\n"
            "Среда:\n09:00 — Химия\n10:40 — История\n"
        )

    def handle_schedule(message: Message):
        users = load_users()
        chat_id = str(message.chat.id)
        user = users.get(chat_id)

        if not user:
            bot.reply_to(message, NOT_REGISTERED)
            return
        if not user.get("group"):
            bot.reply_to(message, NO_GROUP)
            return

        bot.reply_to(message, get_schedule_text(user["group"]))

    @bot.message_handler(commands=["schedule"])
    def schedule_command(message: Message):
        handle_schedule(message)

    @bot.message_handler(func=lambda msg: msg.text == "🗓 Всё расписание")
    def schedule_button(message: Message):
        handle_schedule(message)

    @bot.message_handler(commands=["ping"])
    def ping_handler(message: Message):
        bot.reply_to(message, PING)

    @bot.message_handler(commands=["id"])
    def id_handler(message: Message):
        bot.reply_to(message, f"🆔 Твой chat_id: {message.chat.id}")

    @bot.message_handler(commands=["help"])
    def help_handler(message: Message):
        bot.reply_to(message, HELP_MESSAGE)

    @bot.message_handler(commands=["setgroup"])
    def setgroup_handler(message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, SETGROUP_INSTRUCTION)
            return

        group = parts[1].strip()

        if not re.fullmatch(r"\d+/\d+", group):
            bot.reply_to(message, INVALID_GROUP_FORMAT)
            return

        update_user_group(message.chat.id, group)
        bot.reply_to(message, GROUP_SAVED.format(group=group))

    # ===== FAN MODE =====
    @bot.message_handler(commands=["fan_on"])
    def fan_on_cmd(message: Message):
        set_fan_mode(message.chat.id, True)
        bot.reply_to(message, FAN_ON_MSG)

    @bot.message_handler(commands=["fan_off"])
    def fan_off_cmd(message: Message):
        set_fan_mode(message.chat.id, False)
        bot.reply_to(message, FAN_OFF_MSG)

    @bot.message_handler(commands=["fan"])
    def fan_status_cmd(message: Message):
        enabled = get_fan_mode(message.chat.id)
        status = "ВКЛ" if enabled else "ВЫКЛ"
        bot.send_message(
            message.chat.id,
            FAN_STATUS_FMT.format(status=status),
            parse_mode="HTML",
            reply_markup=build_fan_toggle_kb(enabled)
        )

    @bot.message_handler(func=lambda m: m.text == "🎉 Фан-режим")
    def fan_button(message: Message):
        enabled = get_fan_mode(message.chat.id)
        status = "ВКЛ" if enabled else "ВЫКЛ"
        bot.send_message(
            message.chat.id,
            FAN_STATUS_FMT.format(status=status),
            parse_mode="HTML",
            reply_markup=build_fan_toggle_kb(enabled)
        )

    @bot.callback_query_handler(func=lambda c: c.data in ("fan:on", "fan:off"))
    def fan_toggle(call: types.CallbackQuery):
        enabled = (call.data == "fan:on")
        set_fan_mode(call.from_user.id, enabled)
        new_status = "ВКЛ" if enabled else "ВЫКЛ"
        bot.answer_callback_query(call.id, text=("Включено" if enabled else "Выключено"))
        bot.edit_message_text(
            f"🎛 Статус фан-режима: <b>{new_status}</b>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML",
            reply_markup=build_fan_toggle_kb(enabled)
        )


    @bot.message_handler(func=lambda msg: True)
    def easter_egg_handler(message: Message):
        text = message.text.lower()

        triggers = ["serega pirat", "серега пират", "пират"]

        if any(trigger in text for trigger in triggers):
            bot.send_sticker(
                message.chat.id,
                "CAACAgIAAxkBAAOcaMR5j0knrqDF0s1lONeOhEY2syYAAvsYAAIRSwhLT7Bhl6t0YIo2BA"
            )

    @bot.message_handler(func=lambda msg: True)
    def fallback_handler(message: Message):
        bot.reply_to(message, UNKNOWN_COMMAND)

