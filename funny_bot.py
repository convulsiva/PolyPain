from datetime import datetime as dt
from pprint import pprint

from telebot import TeleBot
from telebot.custom_filters import StateFilter
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from parsers import schedule_parser  # твой модуль с парсером расписания

# ---------------------------
#  Инициализация бота и FSM
# ---------------------------

TOKEN = ""

users: dict[int, str] = {}  # chat_id -> group_name

storage = StateMemoryStorage()
bot = TeleBot(TOKEN, state_storage=storage)

# Подключаем фильтр состояний — БЕЗ ЭТОГО state=... не работает
bot.add_custom_filter(StateFilter(bot))


class RegisterGroupState(StatesGroup):
    group_name = State()


# ---------------------------
#  Хендлеры команд
# ---------------------------


@bot.message_handler(commands=["start", "help"])
def send_welcome(message: Message):
    # Если пользователь уже закрепил группу
    if message.chat.id in users:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        btn = KeyboardButton("Получить расписание на сегодня!")
        markup.add(btn)
        bot.send_message(
            message.chat.id,
            "Я тебя помню 😎\nДавай, выбирай действие!",
            reply_markup=markup,
        )
        return

    # Новый пользователь — предлагаем указать группу
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("Указать группу", callback_data="set_group")
    markup.add(btn)
    bot.send_message(
        message.chat.id,
        "Привет, это бот расписания Политеха!\nДля начала работы закрепи, пожалуйста, свою группу:",
        reply_markup=markup,
    )


# ---------------------------
#  Callback-хендлеры
# ---------------------------


@bot.callback_query_handler(func=lambda call: call.data == "set_group")
def set_group(call: CallbackQuery):
    # Кнопка «Отмена» при вводе группы
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("Отмена", callback_data="cancel")
    markup.add(btn)

    bot.send_message(
        call.message.chat.id,
        "Отправь мне номер своей группы\nПримерный формат: 5130902/40003\nЖду номерок 🤩!",
        reply_markup=markup,
    )

    # Устанавливаем состояние «ввод названия группы»
    bot.set_state(call.from_user.id, RegisterGroupState.group_name, call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel(call: CallbackQuery):
    # Сбрасываем состояние и сообщаем об отмене
    bot.delete_state(call.from_user.id, call.message.chat.id)
    bot.send_message(call.message.chat.id, "Закрепление группы отменено.")


# ---------------------------
#  Обработка состояния ввода группы
# ---------------------------


@bot.message_handler(state=RegisterGroupState.group_name)
def get_group_name(message: Message):
    group_name = message.text.strip()

    # Проверяем, существует ли такая группа
    if not schedule_parser.group_exist(group_name):
        bot.send_message(
            message.chat.id,
            "Такой группы нет 😔\nПопробуй ещё раз или нажми «Отмена».",
        )
        return

    # Сохраняем группу для чата
    users[message.chat.id] = group_name
    bot.send_message(message.chat.id, f"Ура! Группа {group_name} закреплена! 🎉")

    # Выдаём клавиатуру с основным действием
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn = KeyboardButton("Получить расписание на сегодня!")
    markup.add(btn)
    bot.send_message(
        message.chat.id,
        "Теперь можешь получать расписание 😌",
        reply_markup=markup,
    )

    # Сбрасываем состояние
    bot.delete_state(message.from_user.id, message.chat.id)


# ---------------------------
#  Общий хендлер сообщений
# ---------------------------


@bot.message_handler()
def send_msg(message: Message):
    pprint(users)
    # Основная кнопка — получить расписание
    if message.text == "Получить расписание на сегодня!" and message.chat.id in users:
        group_name = users[message.chat.id]
        schedule = schedule_parser.get_daily_schedule(group_name, dt.now().strftime("%Y-%m-%d"))

        if not schedule.lessons:
            bot.send_message(message.chat.id, "Сегодня пар нет 🥳")
            return

        text_lines = []
        for i, lesson in enumerate(schedule.lessons, start=1):
            time_range = (
                f"{lesson.time_start.strftime('%H:%M')}–{lesson.time_end.strftime('%H:%M')}"
            )
            text_lines.append(f"{i}. {lesson.name} | {time_range}")

        bot.send_message(message.chat.id, "\n".join(text_lines))
        return

    # Если сообщение не подошло ни под одно условие
    if message.chat.id not in users:
        # Пользователь ещё не закрепил группу
        markup = InlineKeyboardMarkup()
        btn = InlineKeyboardButton("Указать группу", callback_data="set_group")
        markup.add(btn)
        bot.send_message(
            message.chat.id,
            "Сначала закрепи свою группу 👇",
            reply_markup=markup,
        )
    else:
        bot.send_message(
            message.chat.id,
            "Я тебя не понял 🤔\nНажми кнопку на клавиатуре или команду /help.",
        )


# ---------------------------
#  Запуск бота
# ---------------------------

if __name__ == "__main__":
    bot.infinity_polling()
