from telebot import TeleBot, types
from ..config import Config
from ..keyboards import build_admin_kb
from services.stats_service import get_admin_stats
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
        action = call.data.split("admin:", 1)[1]

        if action == "stats":
            bot.answer_callback_query(call.id)

            stats = get_admin_stats()

            lines = [
                "📊 <b>Статистика</b>",
                f"• Пользователей (всего): <b>{stats['total_users']}</b>",
                f"• Уникальных чатов: <b>{stats['unique_chats']}</b>",
                f"• Администраторов: <b>{stats['admins_count']}</b>",
            ]

            if stats.get("with_group", 0) > 0:
                lines.append(f"• Указали группу: <b>{stats['with_group']}</b>")
            if stats.get("without_group", 0) > 0:
                lines.append(f"• Без группы: <b>{stats['without_group']}</b>")

            group_top = stats.get("group_top") or []
            if group_top:
                top_lines = "\n".join(f"   — <code>{g}</code>: {n}" for g, n in group_top)
                lines.append("• ТОП групп:\n" + top_lines)

            if stats.get("last_registered_at"):
                lines.append(
                    f"• Последняя регистрация: <i>{stats['last_registered_at'].strftime('%Y-%m-%d %H:%M:%S')}</i>"
                )
            if stats.get("last_updated_at"):
                lines.append(
                    f"• Последнее обновление профиля: <i>{stats['last_updated_at'].strftime('%Y-%m-%d %H:%M:%S')}</i>"
                )

            text = "\n".join(lines)

            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=build_admin_kb(),
                parse_mode="HTML",
                disable_web_page_preview=True
            )


        elif action == "dm":
            bot.answer_callback_query(call.id)
            msg = bot.send_message(
                call.message.chat.id,
                "✉️ Введите <b>chat_id</b> получателя (или /cancel):",
                parse_mode="HTML",
            )
            bot.register_next_step_handler(msg, _handle_dm_chat_id)

        elif action.startswith("list"):
            bot.answer_callback_query(call.id)
            page = 1
            parts = action.split(":")
            if len(parts) == 2:
                try:
                    page = int(parts[1])
                except ValueError:
                    page = 1

            ids_sorted = sorted(Config.ADMIN_IDS)
            if not ids_sorted:
                text = "👥 <b>Администраторы</b>:\n—"
                kb = build_admin_kb()
            else:
                items = [_format_admin_item(bot, cid) for cid in ids_sorted]
                page_items, page, pages = _paginate(items, page, per_page=10)
                body = "\n".join(
                    f"{idx}. {row}" for idx, row in enumerate(page_items, start=(page - 1) * 10 + 1)
                )
                base_kb = build_admin_kb()
                kb = _admins_keyboard_for_page(base_kb, page, pages)
                text = f"👥 <b>Администраторы</b> ({len(ids_sorted)}):\n{body}"

            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=kb,
                parse_mode="HTML",
                disable_web_page_preview=True
            )

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
            message.chat.id,
            f"Ок. Кому: <code>{target_chat_id}</code>\nТеперь введите <b>текст сообщения</b> (или /cancel):",
            parse_mode="HTML",
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
                target_chat_id,
                f"📩 <b>Сообщение от администратора</b>\n\n{text}",
                parse_mode="HTML",
            )
            bot.reply_to(
                message,
                f"✅ Отправлено пользователю <code>{target_chat_id}</code>.",
                parse_mode="HTML",
            )
        except Exception as e:
            bot.reply_to(message, f"❌ Не удалось отправить: {e!s}")

        pending_dm_chat.pop(admin_uid, None)

    @bot.callback_query_handler(func=lambda c: c.data == "admin:nop")
    @admin_only(bot)
    def _nop(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)

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
    name = _human_name(chat) if chat else str(chat_id)
    mention = f'<a href="tg://user?id={chat_id}">{name}</a>'
    return f"{mention} • <code>{chat_id}</code>"

def _paginate(items: list[str], page: int, per_page: int = 10) -> tuple[list[str], int, int]:
    total = len(items)
    pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, pages))
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], page, pages

def _admins_keyboard_for_page(base_kb: types.InlineKeyboardMarkup, page: int, pages: int) -> types.InlineKeyboardMarkup:
    if pages <= 1:
        return base_kb
    nav = types.InlineKeyboardMarkup(row_width=3)
    row = []
    if page > 1:
        row.append(types.InlineKeyboardButton("◀️", callback_data=f"admin:list:{page-1}"))
    row.append(types.InlineKeyboardButton(f"{page}/{pages}", callback_data="admin:nop"))
    if page < pages:
        row.append(types.InlineKeyboardButton("▶️", callback_data=f"admin:list:{page+1}"))
    nav.add(*row)
    nav.keyboard.extend(base_kb.keyboard)
    return nav
