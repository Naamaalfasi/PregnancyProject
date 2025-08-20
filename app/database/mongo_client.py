from pydoc import doc
import motor.motor_asyncio
from typing import List, Optional
from datetime import datetime
import json
from bson import json_util
from fastapi import HTTPException

from app.config import settings
from app.models import UserProfile, MedicalDocument, Task
from app.database.data_processing import PregnancyDataProcessor

class MongoDBClient:
    def __init__(self):
        self.client = None
        self.db = None
        self._user_ids_cache = set()
        
    async def connect(self):
        """Connect to MongoDB"""
        self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client.pregnancy_agent
        
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    async def _is_user_id_valid(self, user_id: str) -> bool:
        return user_id not in self._user_ids_cache
            
    # User Profile Methods
    async def create_user_profile(self, profile: UserProfile):
        """Create a new user profile"""

        """user_id: Optional[str] = "None-String"
        name: Optional[str] = "None-String"
        date_of_birth: Optional[str] = "DDMMYYYY"  # Changed to str
        pregnancy_week: Optional[int] = Field(None, ge=1, le=42)
        lmp_date: Optional[str] = "None-String"  # Changed to str
        due_date: Optional[str] = "None-String"  # Changed to str
        height: Optional[float] = 0
        weight: Optional[float] = 0
        blood_type: Optional[str] = "None-String"
        medical_conditions: List[str] = []
        allergies: List[str] = []
        medications: List[str] = []
        medical_documents: List[MedicalDocument] = []
        created_at: datetime = Field(default_factory=datetime.utcnow)
        updated_at: datetime = Field(default_factory=datetime.utcnow) """ 

        profile_dict = profile.dict()

        if not await self._is_user_id_valid(profile_dict["user_id"]):
            raise HTTPException(status_code=400, detail="User ID already exists")

        profile_dict["pregnancy_week"] = PregnancyDataProcessor.calculate_pregnancy_week(profile_dict["lmp_date"])
        profile_dict["due_date"] = PregnancyDataProcessor.calculate_due_date(profile_dict["lmp_date"])
        profile_dict["created_at"] = datetime.utcnow()
        profile_dict["updated_at"] = datetime.utcnow()

        self._user_ids_cache.add(profile_dict["user_id"])
            
        result = await self.db.user_profiles.insert_one(profile_dict)
        return profile_dict
        
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        profile_dict = await self.db.user_profiles.find_one({"user_id": user_id})
        if profile_dict:
            return UserProfile(**profile_dict)
        return None
        
    async def update_user_profile(self, user_id: str, profile: UserProfile) -> Optional[UserProfile]:
        """Update user profile"""
        profile_dict = profile.dict()
        profile_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.user_profiles.replace_one(
            {"user_id": user_id}, 
            profile_dict
        )
        
        if result.modified_count > 0:
            return profile
        return None
        
    # Medical Documents Methods
    async def add_medical_document(self, user_id: str, document: MedicalDocument):
        """Add medical document to user profile"""
        document_dict = document.dict()
        
        # Convert datetime to ISO format
        if document_dict.get('upload_date'):
            document_dict['upload_date'] = document_dict['upload_date'].isoformat()
        
        # Add document to user's medical_documents array
        result = await self.db.user_profiles.update_one(
            {"user_id": user_id},
            {"$push": {"medical_documents": document_dict}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User profile not found or document not added")
        
    async def get_user_documents(self, user_id: str) -> List[MedicalDocument]:
        """Get all medical documents for a user"""
        user = await self.get_user_profile(user_id)
        if user and user.medical_documents:
            return user.medical_documents
        return []
        
    # Tasks Methods
    async def create_task(self, task: Task):
        """Create a new task"""
        task_dict = task.dict()
        task_dict["created_at"] = datetime.utcnow()
        
        await self.db.tasks.insert_one(task_dict)
        return task
        
    async def get_user_tasks(self, user_id: str, completed: Optional[bool] = None) -> List[Task]:
        """Get tasks for user with optional completion filter"""
        filter_query = {"user_id": user_id}
        if completed is not None:
            filter_query["completed"] = completed
            
        cursor = self.db.tasks.find(filter_query)
        tasks = []
        async for task_dict in cursor:
            tasks.append(Task(**task_dict))
        return tasks
        
    async def update_task(self, task_id: str, task_update: dict) -> Optional[Task]:
        """Update task"""
        task_update["updated_at"] = datetime.utcnow()
        
        result = await self.db.tasks.update_one(
            {"task_id": task_id},
            {"$set": task_update}
        )
        
        if result.modified_count > 0:
            # Return updated task
            task_dict = await self.db.tasks.find_one({"task_id": task_id})
            return Task(**task_dict)
        return None
        
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        result = await self.db.tasks.delete_one({"task_id": task_id})
        return result.deleted_count > 0