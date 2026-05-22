from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from telebot import TeleBot, ExceptionHandler

from bot.config import load_config
from bot.db.database import init_db
from bot.db.models import (
    Category,
    Group,
    GroupMember,
    GroupTask,
    Recurrence,
    Reminder,
    Task,
    TaskWizardState,
    User,
)
from bot.handlers.group import register_group_handlers
from bot.handlers.start import register_start_handlers
from bot.handlers.task import register_task_handlers
from bot.logging_config import setup_logging
from bot.services.free_time import FreeTimeService
from bot.services.groups import GroupService
from bot.services.scheduler import ReminderScheduler
from bot.services.tasks import TaskService

log = logging.getLogger(__name__)


class BotExceptionHandler(ExceptionHandler):
    def handle(self, exception: Exception) -> bool:
        log.exception("Unhandled exception in handler: %s", exception)
        return True


def init_models() -> None:
    tables = [
        User,
        Category,
        Task,
        Reminder,
        Recurrence,
        Group,
        GroupMember,
        GroupTask,
        TaskWizardState,
    ]
    for table in tables:
        table.create_table(safe=True)


def main() -> None:
    config = load_config()
    setup_logging(config.log_file_path)
    init_db(config.database_path)
    init_models()

    bot = TeleBot(config.bot_token, exception_handler=BotExceptionHandler())

    jobstores = {
        "default": SQLAlchemyJobStore(url=f"sqlite:///{config.scheduler_db_path}")
    }
    bg_scheduler = BackgroundScheduler(jobstores=jobstores)
    scheduler = ReminderScheduler(bot=bot, scheduler=bg_scheduler)
    scheduler.start()

    free_time_service = FreeTimeService()
    task_service = TaskService(scheduler=scheduler, free_time=free_time_service)
    group_service = GroupService(free_time=free_time_service, task_service=task_service)

    register_start_handlers(bot)
    register_task_handlers(bot, task_service)
    register_group_handlers(bot, group_service)

    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    main()
