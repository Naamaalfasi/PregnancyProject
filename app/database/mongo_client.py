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
from app.database.file_processing import DocumentStatus

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
    
    async def update_user_blood_type(self, user_id: str, blood_type: str):
        """Update user's blood type in profile"""
        result = await self.db.user_profiles.update_one(
            {"user_id": user_id},
            {"$set": {"blood_type": blood_type}}
        )
        
        if result.modified_count > 0:
            print(f"Updated blood type to {blood_type} for user {user_id}")
        else:
            print(f"Failed to update blood type for user {user_id}")
        
        
    async def get_user_documents(self, user_id: str) -> List[MedicalDocument]:
        """Get all medical documents for a user"""
        user = await self.get_user_profile(user_id)
        if user and user.medical_documents:
            return user.medical_documents
        return []
        

    async def update_document_status(self, user_id: str, document_id: str, status: DocumentStatus):
        """Update document status"""
        result = await self.db.user_profiles.update_one(
            {"user_id": user_id, "medical_documents.document_id": document_id},
            {"$set": {"medical_documents.$.status": status}}
        )
        return result.modified_count > 0
    
    async def update_document_summary(self, user_id: str, document_id: str, summary: str):
        """Update document summary after processing"""
        result = await self.db.user_profiles.update_one(
            {"user_id": user_id, "medical_documents.document_id": document_id},
            {"$set": {"medical_documents.$.summary": summary}}
        )
        return result.modified_count > 0
    
    async def get_medical_document(self, user_id: str, document_id: str) -> Optional[MedicalDocument]:
        """Get medical document by user ID and document ID"""
        user = await self.get_user_profile(user_id)
        if user and user.medical_documents:
            for doc in user.medical_documents:
                if doc.document_id == document_id:
                    return doc
        return None


    async def update_user_profile_with_medical_data(self, user_id: str, parsed_medical_data: dict):
        """Update user profile with extracted medical data from documents"""
        user = await self.get_user_profile(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        update_fields = {}
        
        # Extract and validate medical data fields
        medical_fields = {
            'blood_type': ('blood_type', "None-String"),
            'height': ('height', 0),
            'weight': ('weight', 0),
            'allergies': ('allergies', []),
            'medications': ('medications', [])
        }
        
        for field_name, (db_field, default_value) in medical_fields.items():
            extracted_value = parsed_medical_data.get(field_name)
            if extracted_value and extracted_value != 'None':
                if field_name in ['allergies', 'medications']:
                    # For list fields, always update if we have data
                    update_fields[db_field] = extracted_value
                else:
                    # For scalar fields, only update if current value is default
                    current_value = getattr(user, db_field)
                    if current_value == default_value:
                        update_fields[db_field] = extracted_value
        
        # Update user profile if we have new profile-level fields
        if update_fields:
            update_fields['updated_at'] = datetime.utcnow()
            await self.db.user_profiles.update_one(
                {"user_id": user_id},
                {"$set": update_fields}
            )

        return len(update_fields) > 0
    
    # Medical Document Methods
    async def add_medical_document(self, user_id: str, document: MedicalDocument, parsed_medical_data: dict):
        """Add medical document to user profile and update user profile with new data"""
        document_dict = document.dict()
        
        # Convert datetime to ISO format
        if document_dict.get('upload_date'):
            document_dict['upload_date'] = document_dict['upload_date'].isoformat()
        
        # Update user profile with extracted medical data (if any)
        if parsed_medical_data:
            await self.update_user_profile_with_medical_data(user_id, parsed_medical_data)
        
        # Add document to user's medical_documents array
        result = await self.db.user_profiles.update_one(
            {"user_id": user_id},
            {"$push": {"medical_documents": document_dict}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User profile not found or document not added")    


    async def update_document_with_medical_data(self, user_id: str, document_id: str, parsed_medical_data: dict, summary: str):
        """Update existing document with extracted medical data and update user profile"""
        # Update user profile with extracted medical data
        await self.update_user_profile_with_medical_data(user_id, parsed_medical_data)
        await self.update_document_summary(user_id, document_id, summary)
        return True


