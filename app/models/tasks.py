from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskType(str, Enum):
    MEDICAL_CHECKUP = "medical_checkup"
    TEST = "test"
    PREPARATION = "preparation"
    SHOPPING = "shopping"
    DOCUMENTATION = "documentation"
    EMERGENCY = "emergency"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(BaseModel):
    task_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    task_type: TaskType
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    pregnancy_week: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)