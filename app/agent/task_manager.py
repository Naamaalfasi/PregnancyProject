import json
from pathlib import Path
from app.models.tasks import Task, TaskType, TaskPriority, TaskSource, TaskReason
from datetime import datetime, timedelta, date
import uuid
from app.database.mongo_client import MongoDBClient

class TaskManager:
    def __init__(self, mongo_client: MongoDBClient):
        self.mongo_client = mongo_client

    def load_standard_tasks(self):
        path = Path("app/data/standard_tasks.json")
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def check_conditions(self, conditions, user_profile):
        if not conditions:
            return True
        for condition in conditions:
            field = condition["field"]
            operator = condition["operator"]
            value = condition["value"]
            # user_profile יכול להיות אובייקט Pydantic או dict
            user_value = getattr(user_profile, field, None)
            if user_value is None and isinstance(user_profile, dict):
                user_value = user_profile.get(field, None)
            if operator == "equals" and user_value != value:
                return False
            if operator == "not_equals" and user_value == value:
                return False
        return True

    def find_existing_task(self, tasks, user_id, task_type, title):
        for task in tasks:
            if (
                task.user_id == user_id and
                task.task_type == task_type and
                task.title == title
            ):
                return task
        return None

    def create_task(
        user_id: str,
        title: str,
        description: str,
        task_type: TaskType,
        priority: TaskPriority,
        start_week: int,
        end_week: int,
        source: TaskSource = TaskSource.AGENT,
        reason: TaskReason = TaskReason.STANDARD_SCHEDULE,
        notes: str = "",
    ) -> Task:
        return Task(
            task_id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            start_week=start_week,
            end_week=end_week,
            source=source,
            reason=reason,
            related_links=None,
            result=None,
            notes=notes
        )

    async def create_standard_tasks_for_user(self, user_id):
        # שליפת פרופיל המשתמש
        user = await self.mongo_client.get_user_profile(user_id)
        if not user:
            raise ValueError("User not found")
        current_week = user.pregnancy_week

        standard_tasks = self.load_standard_tasks()
        tasks = []
        for item in standard_tasks:
            conditions = item.get("condition", [])
            if not self.check_conditions(conditions, user):
                continue
            for recurring in item.get("recurring", []):
                start_week = recurring["start_week"]
                end_week = recurring.get("end_week", start_week)
                notes = item.get("notes", "")
                task = Task(
                    task_id=str(uuid.uuid4()),
                    user_id=user_id,
                    title=item["title"],
                    description=item.get("description"),
                    task_type=TaskType(item["task_type"]),
                    priority=TaskPriority(item["priority"]),
                    start_week=start_week,
                    end_week=end_week,
                    source=TaskSource.AGENT,
                    reason=TaskReason.STANDARD_SCHEDULE,
                    notes=notes
                )
                tasks.append(task)
        return tasks

    def update_or_create_task(self, tasks, user_id, title, description, task_type, priority, start_week, end_week, source, reason, notes):
        existing_task = TaskManager.find_existing_task(tasks, user_id, task_type, title)
        if existing_task:
            existing_task.start_week = start_week
            existing_task.end_week = end_week
            existing_task.reason = reason
            existing_task.notes = notes
            # אפשר להוסיף לוגיקה לשמירת היסטוריית שינויים
            return existing_task
        else:
            return TaskManager.create_task(
                user_id=user_id,
                title=title,
                description=description,
                task_type=task_type,
                priority=priority,
                start_week=start_week,
                end_week=end_week,
                source=source,
                reason=reason,
                notes=notes
            )

    def parse_european_date(self, date_str: str) -> date:
        """המרת תאריך מ-DD/MM/YYYY ל-YYYY-MM-DD"""
        day, month, year = date_str.split("/")
        return date(int(year), int(month), int(day))