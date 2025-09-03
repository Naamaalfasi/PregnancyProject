from app.models.tasks import Task, TaskType, TaskPriority, TaskSource, TaskReason
from datetime import datetime, timedelta

def find_existing_task(tasks, user_id, task_type, title):
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
    pregnancy_week: int,
    due_date: datetime,
    source: TaskSource = TaskSource.AGENT,
    reason: TaskReason = TaskReason.STANDARD_SCHEDULE,
    notes: str = "",
) -> Task:
    return Task(
        task_id=generate_task_id(),
        user_id=user_id,
        title=title,
        description=description,
        task_type=task_type,
        priority=priority,
        pregnancy_week=pregnancy_week,
        due_date=due_date,
        source=source,
        reason=reason,
        related_links=None,
        result=None,
        # ... שדות נוספים ...
    )

def create_standard_tasks_for_user(user_id: str, pregnancy_start_date: datetime):
    tasks = []
    for item in STANDARD_PREGNANCY_TASKS:
        week = item["pregnancy_week"]
        due_date = pregnancy_start_date + timedelta(weeks=week-1)
        task = create_task(
            user_id=user_id,
            title=item["title"],
            description=item["description"],
            task_type=item["task_type"],
            priority=item["priority"],
            pregnancy_week=week,
            due_date=due_date,
            source=TaskSource.AGENT,
            reason=TaskReason.STANDARD_SCHEDULE,
            notes=item.get("notes", "")
        )
        tasks.append(task)
    return tasks

def update_or_create_task(tasks, user_id, title, description, task_type, priority, pregnancy_week, due_date, source, reason, notes):
    existing_task = find_existing_task(tasks, user_id, task_type, title)
    if existing_task:
        # עדכון מטלה קיימת (למשל הקדמת שבוע/תאריך)
        existing_task.pregnancy_week = pregnancy_week
        existing_task.due_date = due_date
        existing_task.reason = reason
        existing_task.notes = notes
        # אפשר להוסיף לוגיקה לשמירת היסטוריית שינויים
        return existing_task
    else:
        # יצירת מטלה חדשה
        return create_task(
            user_id=user_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            pregnancy_week=pregnancy_week,
            due_date=due_date,
            source=source,
            reason=reason,
            notes=notes
        )