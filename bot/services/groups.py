from __future__ import annotations

from dataclasses import dataclass

from telebot.types import Message

import json

from bot.db.models import Group, GroupMember, TaskWizardState
from bot.services.free_time import FreeTimeService
from bot.services.tasks import TaskService
from bot.services.users import ensure_user
from bot.utils.time_parse import DATE_TIME_FORMAT, parse_datetime


@dataclass
class GroupService:
    free_time: FreeTimeService
    task_service: TaskService

    def create_group(self, message: Message) -> str:
        user = ensure_user(message.from_user)
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return "👥 Нужно имя группы. Пример: /group_create Название"
        name = parts[1].strip()
        group = Group.create(name=name)
        GroupMember.create(group=group, user=user, is_admin=True)
        return f"✅ Группа создана. id={group.id}"

    def join_group(self, message: Message) -> str:
        user = ensure_user(message.from_user)
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return "Нужен id группы. Пример: /group_join 123"
        group_id = int(parts[1])
        group = Group.get_by_id(group_id)
        GroupMember.get_or_create(group=group, user=user, defaults={"is_admin": False})
        return "🎉 Вы присоединились к группе"

    def add_group_task(self, message: Message) -> str:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return "Нужен id группы. Пример: /group_add_task 123"
        group_id = int(parts[1])
        user = ensure_user(message.from_user)
        if not GroupMember.select().where(
            (GroupMember.group == group_id)
            & (GroupMember.user == user)
            & (GroupMember.is_admin == True)
        ).exists():
            return "⛔ Нет прав администратора"
        payload = {"step": "type", "is_group": True, "group_id": group_id}
        TaskWizardState.insert(
            user=user,
            step="type",
            payload=json.dumps(payload),
        ).on_conflict(
            conflict_target=[TaskWizardState.user],
            update={TaskWizardState.step: "type", TaskWizardState.payload: json.dumps(payload)},
        ).execute()
        return (
            "👥 Создаем групповую задачу!\n"
            "Выберите тип ниже или напишите: one_time | recurring | deadline"
        )

    def group_free_time(self, message: Message) -> str:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            return "Нужны id группы и дата. Пример: /group_free 123 24.05.2026 00:00"
        group_id = int(parts[1])
        try:
            day = parse_datetime(parts[2])
        except ValueError:
            return "Неверный формат даты. Пример: 24.05.2026 18:30"
        members = GroupMember.select().where(GroupMember.group == group_id)
        intervals = [self.free_time.get_free_intervals(m.user.id, day) for m in members]
        free = self.free_time.intersect_intervals(intervals)
        if not free:
            return "⛔ Свободного времени нет"
        lines = [
            f"🟢 {start.strftime(DATE_TIME_FORMAT)} - {end.strftime(DATE_TIME_FORMAT)}"
            for start, end in free
        ]
        return "🕒 Совместные свободные окна:\n" + "\n".join(lines)
