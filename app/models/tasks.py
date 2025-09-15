from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskType(str, Enum):
    MEDICAL_CHECKUP = "Medical_checkup"
    TEST = "Test"
    PREPARATION = "Preparation"
    SHOPPING = "Shopping"
    DOCUMENTATION = "Documentation"
    EMERGENCY = "Emergency"

class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

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
    updated_at: Optional[datetime] = None

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

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[str] = None
    priority: Optional[str] = None
    pregnancy_week: Optional[int] = None
    due_date: Optional[datetime] = None
    source: Optional[str] = None
    reason: Optional[str] = None
    related_links: Optional[List[str]] = None
    notes: Optional[str] = None
    # אפשר להוסיף עוד שדות אם צריך