from __future__ import annotations

from telebot import TeleBot
from telebot.types import Message

from bot.services.users import ensure_user, set_active_end, set_active_start, set_user_timezone


def register_start_handlers(bot: TeleBot) -> None:
    @bot.message_handler(commands=["start", "help"])
    def handle_start(message: Message) -> None:
        ensure_user(message.from_user)
        bot.reply_to(
            message,
            "Привет! Я помогу держать дела под контролем. Вот быстрые команды:\n"
            "➕ /add — новая задача\n"
            "📅 /list day — задачи на день\n"
            "🏷️ /list category — задачи по категориям\n"
            "⏳ /free — свободное время на дату\n"
            "🧹 /delete 1 или /delete 2,3 или /delete 1-5 — удалить\n"
            "🔕 /unmute 1 — вернуть заглушенную повторяющуюся\n"
            "👥 /group_create, /group_join, /group_add_task, /group_free — группы\n"
            "🌍 /timezone Europe/Moscow — таймзона\n"
            "🕘 /active_start 9 и /active_end 22 — часы активности",
        )

    @bot.message_handler(commands=["timezone"])
    def handle_timezone(message: Message) -> None:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "🌍 Укажите таймзону. Пример: /timezone Europe/Moscow")
            return
        response = set_user_timezone(message.from_user.id, parts[1].strip())
        bot.reply_to(message, response)

    @bot.message_handler(commands=["active_start"])
    def handle_active_start(message: Message) -> None:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "🕘 Укажите час начала. Пример: /active_start 9")
            return
        try:
            hour = int(parts[1].strip())
        except ValueError:
            bot.reply_to(message, "Неверный формат. Пример: /active_start 9")
            return
        response = set_active_start(message.from_user.id, hour)
        bot.reply_to(message, response)

    @bot.message_handler(commands=["active_end"])
    def handle_active_end(message: Message) -> None:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "🕙 Укажите час конца. Пример: /active_end 22")
            return
        try:
            hour = int(parts[1].strip())
        except ValueError:
            bot.reply_to(message, "Неверный формат. Пример: /active_end 22")
            return
        response = set_active_end(message.from_user.id, hour)
        bot.reply_to(message, response)
