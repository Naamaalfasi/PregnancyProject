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
    extracted_data: Optional[dict] = None
    is_processed: bool = False

class UserProfile(BaseModel):
    user_id: str
    name: Optional[str] = None
    date_of_birth: Optional[int] = None
    pregnancy_week: Optional[int] = Field(None, ge=1, le=42)
    lmp_date: Optional[date] = None  # Last Menstrual Period
    due_date: Optional[date] = None
    height: Optional[float] = None  # in cm
    weight: Optional[float] = None  # in kg
    blood_type: Optional[str] = None
    medical_conditions: List[str] = []
    allergies: List[str] = []
    medications: List[str] = []
    emergency_contact: Optional[str] = None
    medical_documents: List[MedicalDocument] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }