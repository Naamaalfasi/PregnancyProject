import motor.motor_asyncio
from typing import List, Optional
from datetime import datetime
import json

from app.config import settings
from app.models import UserProfile, MedicalDocument, Task

class MongoDBClient:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client.pregnancy_agent
        
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            
    # User Profile Methods
    async def create_user_profile(self, profile: UserProfile):
        """Create a new user profile"""
        profile_dict = profile.dict()
        profile_dict["created_at"] = datetime.utcnow()
        profile_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.user_profiles.insert_one(profile_dict)
        return profile
        
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
        
        # Add document to user's medical_documents array
        await self.db.user_profiles.update_one(
            {"user_id": user_id},
            {"$push": {"medical_documents": document_dict}}
        )
        
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