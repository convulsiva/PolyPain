from telebot import TeleBot, types
from telebot.apihelper import ApiTelegramException

from ..config import Config
from ..keyboards import build_admin_kb
from ..services import admin_service, stats_service
from .guards import admin_only, is_admin


def register_admin_handlers(bot: TeleBot):
    pending_dm_chat: dict[int, int] = {}

    @bot.message_handler(commands=["admin"])
    @admin_only(bot)
    def admin_entry(message: types.Message):
        bot.send_message(
            message.chat.id,
            "🛡 <b>Админ-панель PolyPain</b>\nВыбери действие:",
            reply_markup=build_admin_kb(),
            parse_mode="HTML",
        )

    @bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("admin:"))
    @admin_only(bot)
    def on_admin_action(call: types.CallbackQuery):
        action_parts = call.data.split(":")
        action = action_parts[1]

        if action == "stats":
            bot.answer_callback_query(call.id)
            stats = stats_service.get_admin_stats()
            all_admin_ids = set(Config.ADMIN_IDS) | admin_service.load_admins()
            lines = [
                "📊 <b>Статистика</b>",
                f"• Пользователей (всего): <b>{stats['total_users']}</b>",
                f"• Уникальных чатов: <b>{stats['unique_chats']}</b>",
                f"• Администраторов: <b>{len(all_admin_ids)}</b>",
            ]
            if stats.get("with_group", 0) > 0:
                lines.append(f"• Указали группу: <b>{stats['with_group']}</b>")
            group_top = stats.get("group_top") or []
            if group_top:
                top_lines = "\n".join(f"   — <code>{g}</code>: {n}" for g, n in group_top)
                lines.append("• ТОП групп:\n" + top_lines)

            text = "\n".join(lines)
            bot.edit_message_text(
                text, chat_id=call.message.chat.id, message_id=call.message.message_id,
                reply_markup=build_admin_kb(), parse_mode="HTML", disable_web_page_preview=True
            )
        elif action == "dm":
            bot.answer_callback_query(call.id)
            msg = bot.send_message(
                call.message.chat.id, "✉️ Введите <b>chat_id</b> получателя (или /cancel):", parse_mode="HTML"
            )
            bot.register_next_step_handler(msg, _handle_dm_chat_id)
        elif action == "list":
            bot.answer_callback_query(call.id)
            page = int(action_parts[2]) if len(action_parts) > 2 else 1
            _send_admin_list_page(bot, call, page)
        elif action == "add":
            bot.answer_callback_query(call.id)
            msg = bot.send_message(
                call.message.chat.id, "Введите <b>ID пользователя</b>, которого хотите сделать админом (или /cancel):", parse_mode="HTML"
            )
            bot.register_next_step_handler(msg, _handle_add_admin_id)
        elif action == "remove_by_id":
            bot.answer_callback_query(call.id)
            msg = bot.send_message(
                call.message.chat.id, "Введите <b>ID пользователя</b>, которого хотите лишить прав администратора (или /cancel):", parse_mode="HTML"
            )
            bot.register_next_step_handler(msg, _handle_remove_admin_id)
        elif action == "back_to_menu":
            bot.answer_callback_query(call.id)
            bot.edit_message_text(
                "🛡 <b>Админ-панель PolyPain</b>\nВыбери действие:",
                chat_id=call.message.chat.id, message_id=call.message.message_id,
                reply_markup=build_admin_kb(), parse_mode="HTML"
            )

    def _handle_add_admin_id(message: types.Message):
        if not is_admin(message.from_user.id): return
        text = (message.text or "").strip()
        if text.lower() == "/cancel":
            bot.reply_to(message, "Отменено.")
            admin_entry(message)
            return
        try:
            target_user_id = int(text)
            if admin_service.add_admin(target_user_id):
                bot.reply_to(message, f"✅ Пользователь <code>{target_user_id}</code> успешно назначен администратором.", parse_mode="HTML")
            else:
                bot.reply_to(message, f"⚠️ Пользователь <code>{target_user_id}</code> уже является администратором.", parse_mode="HTML")
        except ValueError:
            msg = bot.reply_to(message, "❗️Неверный ID. Пожалуйста, введите число или /cancel:")
            bot.register_next_step_handler(msg, _handle_add_admin_id)
            return
        admin_entry(message)

    def _handle_remove_admin_id(message: types.Message):
        if not is_admin(message.from_user.id): return
        text = (message.text or "").strip()
        if text.lower() == "/cancel":
            bot.reply_to(message, "Отменено.")
            admin_entry(message)
            return
        try:
            target_user_id = int(text)
            if target_user_id in Config.ADMIN_IDS:
                bot.reply_to(message, "⛔️ Супер-администратора нельзя удалить этим способом.")
                admin_entry(message)
                return
            if admin_service.remove_admin(target_user_id):
                bot.reply_to(message, f"✅ Пользователь <code>{target_user_id}</code> больше не является администратором.", parse_mode="HTML")
            else:
                bot.reply_to(message, f"⚠️ Пользователь <code>{target_user_id}</code> не был найден в списке администраторов.", parse_mode="HTML")
        except ValueError:
            msg = bot.reply_to(message, "❗️Неверный ID. Пожалуйста, введите число или /cancel:")
            bot.register_next_step_handler(msg, _handle_remove_admin_id)
            return
        admin_entry(message)

    def _handle_dm_chat_id(message: types.Message):
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "⛔️ Нет доступа.")
            return
        text = (message.text or "").strip()
        if text.lower() == "/cancel":
            bot.reply_to(message, "Отменено.")
            return
        try:
            target_chat_id = int(text)
        except ValueError:
            msg = bot.reply_to(message, "❗️ Неверный chat_id. Введите число или /cancel:")
            bot.register_next_step_handler(msg, _handle_dm_chat_id)
            return
        pending_dm_chat[message.from_user.id] = target_chat_id
        msg = bot.send_message(
            message.chat.id, f"Ок. Кому: <code>{target_chat_id}</code>\nТеперь введите <b>текст сообщения</b> (или /cancel):", parse_mode="HTML"
        )
        bot.register_next_step_handler(msg, _handle_dm_text)

    def _handle_dm_text(message: types.Message):
        admin_uid = message.from_user.id
        if not is_admin(admin_uid):
            bot.reply_to(message, "⛔️ Нет доступа.")
            return
        text = (message.text or "").strip()
        if text.lower() == "/cancel":
            pending_dm_chat.pop(admin_uid, None)
            bot.reply_to(message, "Отменено.")
            return
        if not text:
            msg = bot.reply_to(message, "❗️ Пустое сообщение. Введите текст или /cancel:")
            bot.register_next_step_handler(msg, _handle_dm_text)
            return
        target_chat_id = pending_dm_chat.get(admin_uid)
        if target_chat_id is None:
            msg = bot.reply_to(message, "Сессия отправки потеряна. Введите chat_id (или /cancel):")
            bot.register_next_step_handler(msg, _handle_dm_chat_id)
            return
        try:
            bot.send_message(
                target_chat_id, f"📩 <b>Сообщение от администратора</b>\n\n{text}", parse_mode="HTML"
            )
            bot.reply_to(
                message, f"✅ Отправлено пользователю <code>{target_chat_id}</code>.", parse_mode="HTML"
            )
        except Exception as e:
            bot.reply_to(message, f"❌ Не удалось отправить: {e!s}")
        pending_dm_chat.pop(admin_uid, None)

    @bot.callback_query_handler(func=lambda c: c.data == "admin:nop")
    @admin_only(bot)
    def _nop(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)

def _send_admin_list_page(bot: TeleBot, call: types.CallbackQuery, page: int = 1):
    all_admin_ids = sorted(list(set(Config.ADMIN_IDS) | admin_service.load_admins()))
    if not all_admin_ids:
        text = "👥 <b>Администраторы</b>:\n—"
        kb = build_admin_kb()
    else:
        page_ids, page, pages = _paginate(all_admin_ids, page, per_page=5)
        body_lines = []
        kb = types.InlineKeyboardMarkup(row_width=1)
        start_index = (page - 1) * 5 + 1
        for i, admin_id in enumerate(page_ids, start=start_index):
            text_line = _format_admin_item(bot, admin_id)
            body_lines.append(f"{i}. {text_line}")
        nav_row = []
        if page > 1:
            nav_row.append(types.InlineKeyboardButton("◀️ Назад", callback_data=f"admin:list:{page - 1}"))
        if pages > 1:
            nav_row.append(types.InlineKeyboardButton(f"📄 {page}/{pages}", callback_data="admin:nop"))
        if page < pages:
            nav_row.append(types.InlineKeyboardButton("▶️ Вперёд", callback_data=f"admin:list:{page + 1}"))
        if nav_row:
            kb.row(*nav_row)
        kb.row(types.InlineKeyboardButton("⬅️ Назад в админ-панель", callback_data="admin:back_to_menu"))
        body = "\n".join(body_lines)
        text = f"👥 <b>Администраторы</b> ({len(all_admin_ids)}):\n{body}"
    try:
        bot.edit_message_text(
            text, chat_id=call.message.chat.id, message_id=call.message.message_id,
            reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True
        )
    except ApiTelegramException as e:
        if "message is not modified" in e.description:
            pass  # Игнорируем ожидаемую ошибку
        else:
            raise

def _human_name(chat) -> str:
    if getattr(chat, "username", None):
        return f"@{chat.username}"
    fn = getattr(chat, "first_name", "") or ""
    ln = getattr(chat, "last_name", "") or ""
    full = (fn + " " + ln).strip()
    return full or "Без имени"

def _format_admin_item(bot: TeleBot, chat_id: int) -> str:
    chat = None
    try:
        chat = bot.get_chat(chat_id)
    except Exception:
        pass
    name = _human_name(chat) if chat else "Неизвестный пользователь"
    mention = f'<a href="tg://user?id={chat_id}">{name}</a>'
    text_line = f"{mention} • <code>{chat_id}</code>"
    if chat_id in Config.ADMIN_IDS:
        text_line += " (👑 Супер-админ)"
    return text_line

def _paginate(items: list, page: int, per_page: int = 10) -> tuple[list, int, int]:
    total = len(items)
    pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, pages))
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], page, pages