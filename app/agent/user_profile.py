from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from bson import ObjectId
from app.database.mongo_client import mongo_client
import logging

logger = logging.getLogger(__name__)

class MedicalDocument(BaseModel):
    document_id: str
    doc_type: str
    upload_date: datetime
    document_date: Optional[str] = None
    original_filename: str
    text_length: int
    chunks_count: int
    status: str = "processed"
    metadata: Dict = {}

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
    medical_documents: List[MedicalDocument] = []  # הוספנו רשימת מסמכים
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[int] = None
    pregnancy_week: Optional[int] = Field(None, ge=1, le=42)
    height: Optional[float] = None
    weight: Optional[float] = None
    blood_type: Optional[str] = None
    medical_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    emergency_contact: Optional[str] = None

class UserProfileManager:
    def __init__(self):
        self.collection = mongo_client.get_collection("user_profiles")
        self.documents_collection = mongo_client.get_collection("medical_documents")
    
    async def create_user_profile(self, user_id: str, profile_data: dict) -> UserProfile:
        """Create a new user profile"""
        try:
            profile = UserProfile(user_id=user_id, **profile_data)
            profile_dict = profile.dict()
            profile_dict["_id"] = ObjectId()
            
            result = self.collection.insert_one(profile_dict)
            logger.info(f"Created user profile for user_id: {user_id}")
            return profile
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by user_id"""
        try:
            profile_data = self.collection.find_one({"user_id": user_id})
            if profile_data:
                profile_data["id"] = str(profile_data["_id"])
                return UserProfile(**profile_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            raise
    
    async def update_user_profile(self, user_id: str, update_data: dict) -> Optional[UserProfile]:
        """Update user profile"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = self.collection.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated user profile for user_id: {user_id}")
                return await self.get_user_profile(user_id)
            return None
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            raise
    
    # פונקציות חדשות לניהול מסמכים רפואיים
    
    async def add_medical_document(self, user_id: str, document_data: dict) -> bool:
        """Add medical document to user profile"""
        try:
            # Create MedicalDocument object
            document = MedicalDocument(**document_data)
            
            # Add to user profile
            result = self.collection.update_one(
                {"user_id": user_id},
                {"$push": {"medical_documents": document.dict()}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Added medical document {document.document_id} to user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to add medical document: {e}")
            raise
    
    async def get_user_medical_documents(self, user_id: str, doc_type: Optional[str] = None) -> List[MedicalDocument]:
        """Get all medical documents for a user"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                return []
            
            documents = profile.medical_documents
            
            # Filter by document type if specified
            if doc_type:
                documents = [doc for doc in documents if doc.doc_type == doc_type]
            
            return documents
        except Exception as e:
            logger.error(f"Failed to get user medical documents: {e}")
            raise
    
    async def get_document_summary(self, user_id: str) -> Dict:
        """Get summary of user's medical documents"""
        try:
            documents = await self.get_user_medical_documents(user_id)
            
            summary = {
                "total_documents": len(documents),
                "documents_by_type": {},
                "latest_document": None,
                "has_abnormal_results": False
            }
            
            # Count by type
            for doc in documents:
                doc_type = doc.doc_type
                if doc_type not in summary["documents_by_type"]:
                    summary["documents_by_type"][doc_type] = 0
                summary["documents_by_type"][doc_type] += 1
            
            # Find latest document
            if documents:
                latest_doc = max(documents, key=lambda x: x.upload_date)
                summary["latest_document"] = {
                    "doc_type": latest_doc.doc_type,
                    "upload_date": latest_doc.upload_date,
                    "filename": latest_doc.original_filename
                }
            
            # Check for abnormal results
            for doc in documents:
                if doc.metadata.get("has_abnormal_values", False) or doc.metadata.get("has_abnormalities", False):
                    summary["has_abnormal_results"] = True
                    break
            
            return summary
        except Exception as e:
            logger.error(f"Failed to get document summary: {e}")
            raise
    
    async def remove_medical_document(self, user_id: str, document_id: str) -> bool:
        """Remove medical document from user profile"""
        try:
            result = self.collection.update_one(
                {"user_id": user_id},
                {"$pull": {"medical_documents": {"document_id": document_id}}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Removed medical document {document_id} from user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove medical document: {e}")
            raise
    
    async def calculate_pregnancy_week(self, lmp_date: date) -> int:
        """Calculate current pregnancy week based on LMP"""
        today = date.today()
        days_pregnant = (today - lmp_date).days
        weeks_pregnant = days_pregnant // 7
        return max(1, min(42, weeks_pregnant))
    
    async def get_pregnancy_info(self, user_id: str) -> dict:
        """Get pregnancy-specific information"""
        profile = await self.get_user_profile(user_id)
        if not profile:
            return None
        
        info = {
            "current_week": profile.pregnancy_week,
            "days_until_due": None,
            "trimester": None
        }
        
        if profile.due_date:
            today = date.today()
            days_until_due = (profile.due_date - today).days
            info["days_until_due"] = days_until_due
        
        if profile.pregnancy_week:
            if profile.pregnancy_week <= 13:
                info["trimester"] = "ראשון"
            elif profile.pregnancy_week <= 26:
                info["trimester"] = "שני"
            else:
                info["trimester"] = "שלישי"
        
        return info

# Global user profile manager instance
user_profile_manager = UserProfileManager()