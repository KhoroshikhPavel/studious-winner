from __future__ import annotations

from telebot import TeleBot
from telebot.types import Message

from bot.services.groups import GroupService


def register_group_handlers(bot: TeleBot, group_service: GroupService) -> None:
    @bot.message_handler(commands=["group_create"])
    def handle_group_create(message: Message) -> None:
        response = group_service.create_group(message)
        bot.reply_to(message, response)

    @bot.message_handler(commands=["group_join"])
    def handle_group_join(message: Message) -> None:
        response = group_service.join_group(message)
        bot.reply_to(message, response)

    @bot.message_handler(commands=["group_add_task"])
    def handle_group_add_task(message: Message) -> None:
        response = group_service.add_group_task(message)
        bot.reply_to(message, response)

    @bot.message_handler(commands=["group_free"])
    def handle_group_free(message: Message) -> None:
        response = group_service.group_free_time(message)
        bot.reply_to(message, response)
