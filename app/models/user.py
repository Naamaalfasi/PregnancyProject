from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class DocumentType(str, Enum):
    BLOOD_TEST = "blood_test"
    ULTRASOUND = "ultrasound"
    URINE_TEST = "urine_test"
    GENETIC_TEST = "genetic_test"
    OTHER = "other"

class MedicalDocument(BaseModel):
    document_id: str
    document_type: DocumentType
    upload_date: datetime
    file_name: str
    file_size: int
    summary: Optional[str] = None
    is_processed: bool = False

class UserProfile(BaseModel):
    user_id: Optional[str] = "None-String"
    name: Optional[str] = "None-String"
    date_of_birth: Optional[str] = "None-String"  # Changed to str
    pregnancy_week: Optional[int] = Field(None, ge=1, le=42)
    lmp_date: Optional[str] = "None-String"  # Changed to str
    due_date: Optional[str] = "None-String"  # Changed to str
    height: Optional[float] = 0
    weight: Optional[float] = 0
    blood_type: Optional[str] = "None-String"
    medical_conditions: List[str] = []
    allergies: List[str] = []
    medications: List[str] = []
    emergency_contact: Optional[str] = "None-String"
    medical_documents: List[MedicalDocument] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

    @property
    def lmp_date_as_date(self) -> Optional[date]:
        """Convert lmp_date string to date object"""
        return date.fromisoformat(self.lmp_date) if self.lmp_date else None

    @property
    def due_date_as_date(self) -> Optional[date]:
        """Convert due_date string to date object"""
        return date.fromisoformat(self.due_date) if self.due_date else None

    

