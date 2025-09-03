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

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"

class TaskSource(str, Enum):
    AGENT = "agent"
    USER = "user"

class TaskReason(str, Enum):
    STANDARD_SCHEDULE = "standard_schedule"
    DOCTOR_RECOMMENDATION = "doctor_recommendation"
    TEST_ANALYSIS = "test_analysis"
    OTHER = "other"

class Task(BaseModel):
    task_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    task_type: TaskType
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    pregnancy_week: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source: TaskSource = TaskSource.AGENT
    reason: TaskReason = TaskReason.STANDARD_SCHEDULE
    related_links: Optional[List[str]] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: TaskType
    priority: TaskPriority = TaskPriority.MEDIUM
    pregnancy_week: Optional[int] = None
    due_date: Optional[datetime] = None
    source: TaskSource = TaskSource.USER
    reason: TaskReason = TaskReason.OTHER
    related_links: Optional[List[str]] = None