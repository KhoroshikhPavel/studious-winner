from __future__ import annotations

from pathlib import Path
from peewee import DatabaseProxy, SqliteDatabase

db_proxy = DatabaseProxy()


def init_db(database_path: str) -> SqliteDatabase:
    db_path = Path(database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    database = SqliteDatabase(database_path, pragmas={
        "journal_mode": "wal",
        "foreign_keys": 1,
    })
    db_proxy.initialize(database)
    return database


def get_db() -> DatabaseProxy:
    return db_proxy
