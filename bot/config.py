from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv(os.getenv("DOTENV_PATH", ".env"))


@dataclass(frozen=True)
class AppConfig:
    bot_token: str
    default_timezone: str
    database_path: str
    log_file_path: str
    scheduler_db_path: str


def load_config() -> AppConfig:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    default_timezone = os.getenv("DEFAULT_TIMEZONE", "Europe/Moscow").strip()
    database_path = os.getenv("DATABASE_PATH", "/data/bot.db").strip()
    log_file_path = os.getenv("LOG_FILE_PATH", "/data/logs/bot.log").strip()
    scheduler_db_path = os.getenv("SCHEDULER_DB_PATH", "/data/scheduler.db").strip()

    if not bot_token:
        raise RuntimeError("BOT_TOKEN is required")

    return AppConfig(
        bot_token=bot_token,
        default_timezone=default_timezone,
        database_path=database_path,
        log_file_path=log_file_path,
        scheduler_db_path=scheduler_db_path,
    )
