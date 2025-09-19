
import motor.motor_asyncio
from typing import List, Optional
from datetime import datetime
import uuid
from app.config import settings
from app.models import UserProfile, MedicalDocument, Task, DocumentType
from app.models.chat import Conversation, ChatMessage
from app.database.data_processing import PregnancyDataProcessor
from app.database.file_processing import DocumentStatus
from app.utils.password_utils import hash_password, verify_password
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

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
    
    async def update_one(self, user_id: str, field: str, value: str):
        """Update one field in a document"""
        await self.db.user_profiles.update_one({"user_id": user_id}, {"$set": {field: value}})
        return True

    async def _is_user_id_valid(self, user_id: str) -> bool:
        return user_id not in self._user_ids_cache


    # User Profile Methods
    async def create_user_profile(self, profile: UserProfile):
        """Create a new user profile"""

        profile_dict = profile.dict()

        if not await self._is_user_id_valid(profile_dict["user_id"]):
            return None

        # צור user_id חדש
        profile_dict["user_id"] = str(uuid.uuid4())

        # בדיקת ייחודיות אימייל
        existing = await self.db.user_profiles.find_one({"email": profile_dict["email"]})
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")

        profile_dict["password"] = hash_password(profile_dict["password"])
        profile_dict["pregnancy_week"] = PregnancyDataProcessor.calculate_pregnancy_week(profile_dict["lmp_date"])
        profile_dict["due_date"] = PregnancyDataProcessor.calculate_due_date(profile_dict["lmp_date"])
        profile_dict["age"] = PregnancyDataProcessor.calculate_age(profile_dict["date_of_birth"])
        profile_dict["tasks"] = []
        profile_dict["created_at"] = datetime.utcnow()
        profile_dict["updated_at"] = datetime.utcnow()

        self._user_ids_cache.add(profile_dict["user_id"])
            
        try:
            await self.db.user_profiles.insert_one(profile_dict)
        except DuplicateKeyError:
            # במקרה הנדיר של user_id כפול, נסה שוב פעם אחת
            profile_dict["user_id"] = str(uuid.uuid4())
            try:
                await self.db.user_profiles.insert_one(profile_dict)
            except DuplicateKeyError:
                raise HTTPException(status_code=500, detail="Failed to generate unique user_id")

        return UserProfile(**profile_dict)
    

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        profile_dict = await self.db.user_profiles.find_one({"user_id": user_id})
        if profile_dict:
            return UserProfile(**profile_dict)
        return None

    async def create_conversation(self, user_id: str, conversation: Conversation):
        """Create a new conversation"""
        conversation_dict = conversation.dict()
        await self.db.user_profiles.update_one({"user_id": user_id}, {"$push": {"conversations": conversation_dict}})
        await self.set_active_conversation(user_id, conversation_dict["conversation_id"])
        return True

    async def add_message_to_conversation(self, user_id: str, conversation_id: str, message: ChatMessage):
        """Add a message to a conversation"""
        message_dict = message.dict()
        await self.db.user_profiles.update_one(
            {"user_id": user_id, "conversations.conversation_id": conversation_id},
            {
                "$push": {"conversations.$.messages": message_dict},
                "$set": {"conversations.$.updated_at": datetime.utcnow()}
            }
        )
        return True     
    
    async def set_active_conversation(self, user_id: str, conversation_id: str):
        """Set active conversation"""
        await self.db.user_profiles.update_one(
            {"user_id": user_id},
            {"$set": {"current_conversation": conversation_id}}
        )
        return True

    async def get_active_conversation(self, user_id: str) -> Optional[Conversation]:
        """Get active conversation"""
        user_profile = await self.get_user_profile(user_id)
        if user_profile and user_profile.current_conversation:
            return await self.get_conversation(user_id, user_profile.current_conversation)
        return None
    
    async def get_conversation(self, user_id: str, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        user_profile = await self.get_user_profile(user_id)
        if user_profile and user_profile.conversations:
            for conversation in user_profile.conversations:
                if conversation.conversation_id == conversation_id:
                    return conversation
        return None
    
    async def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get user conversations"""
        user_profile = await self.get_user_profile(user_id)  # Returns UserProfile object
        if user_profile and user_profile.conversations:
            return user_profile.conversations
        return []

    async def verify_password(self, user_id: str, password: str) -> bool:
        """Verify password"""
        profile = await self.get_user_profile(user_id)
        if profile:
            return verify_password(password, profile.password)
        return False

    async def change_password(self, user_id: str, oldPassword: str, newPassword: str) -> bool:
        """Change password"""
        profile = await self.get_user_profile(user_id)
        if profile:
            if verify_password(oldPassword, profile.password):
                profile.password = hash_password(newPassword)
                await self.update_user_profile(user_id, profile)
                return True
        return False

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


    async def get_all_users(self) -> List[UserProfile]:
        """Get all user profiles"""
        cursor = self.db.user_profiles.find({})
        users = []
        async for user_dict in cursor:
            users.append(UserProfile(**user_dict))
        return users

    async def update_all_users_calculated_fields(self) -> dict:
        """Update calculated fields for all users based on current date"""
        updated_count = 0
        error_count = 0
        errors = []
        
        # Define fields to calculate and their calculation functions
        calculated_fields = {
            "pregnancy_week": {
                "dependency": "lmp_date",
                "calculator": PregnancyDataProcessor.calculate_pregnancy_week,
                "required": True
            },
            "due_date": {
                "dependency": "lmp_date", 
                "calculator": PregnancyDataProcessor.calculate_due_date,
                "required": True
            },
            "age": {
                "dependency": "date_of_birth",
                "calculator": PregnancyDataProcessor.calculate_age,
                "required": False  # Age can be None if date_of_birth is missing
            }
        }
        
        # Get all users
        cursor = self.db.user_profiles.find({})
        
        async for user_dict in cursor:
            try:
                user_id = user_dict.get("user_id")
                if not user_id:
                    error_count += 1
                    errors.append("User missing user_id")
                    continue
                
                # Prepare update fields
                update_fields = {"updated_at": datetime.utcnow()}
                user_errors = []
                
                # Calculate each field
                for field_name, field_config in calculated_fields.items():
                    dependency_field = field_config["dependency"]
                    calculator_func = field_config["calculator"]
                    is_required = field_config["required"]
                    
                    dependency_value = user_dict.get(dependency_field)
                    
                    # Check if dependency field exists and is valid
                    if not dependency_value or dependency_value in ["None-String", "0", None]:
                        if is_required:
                            user_errors.append(f"Missing or invalid {dependency_field} for {field_name}")
                            continue
                        else:
                            # Optional field - set to None
                            update_fields[field_name] = None
                            continue
                    
                    # Calculate the field value
                    try:
                        calculated_value = calculator_func(dependency_value)
                        update_fields[field_name] = calculated_value
                        
                    except Exception as calc_error:
                        user_errors.append(f"Error calculating {field_name}: {str(calc_error)}")
                        continue
                
                # If there are errors for this user, skip update
                if user_errors:
                    error_count += 1
                    errors.extend([f"User {user_id}: {error}" for error in user_errors])
                    continue
                
                # Update the user's calculated fields
                result = await self.db.user_profiles.update_one(
                    {"user_id": user_id},
                    {"$set": update_fields}
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    updated_fields_str = ", ".join([f"{k}={v}" for k, v in update_fields.items() if k != "updated_at"])
                    print(f"Updated {updated_fields_str} for user {user_id}")
                else:
                    error_count += 1
                    errors.append(f"User {user_id}: No changes made")
                    
            except Exception as e:
                error_count += 1
                errors.append(f"User {user_id}: {str(e)}")
                print(f"Error updating user {user_id}: {str(e)}")
        
        return {
            "total_users_processed": updated_count + error_count,
            "successfully_updated": updated_count,
            "errors": error_count,
            "error_details": errors,
            "calculated_fields": list(calculated_fields.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }    
    async def create_task(self, user_id: str, task: Task):
        """Add a task to the user's profile (embedded array)"""
        task_dict = task.dict()
        result = await self.db.user_profiles.update_one(
            {"user_id": user_id},
            {"$push": {"tasks": task_dict}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User profile not found or task not added")
        return task_dict["task_id"]

    async def update_user_tasks(self, user_id: str, tasks: list):
        """
        עדכון כל רשימת המטלות של המשתמש
        """
        result = await self.db.user_profiles.update_one(
            {"user_id": user_id},
            {"$set": {"tasks": tasks, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def get_user_tasks(self, user_id: str):
        """
        מחזיר את כל המטלות של המשתמש
        """
        user = await self.get_user_profile(user_id)
        if user and hasattr(user, "tasks"):
            return user.tasks
        return []


    async def update_task(self, task_id: str, task_update: dict):
        """
        עדכון מטלה בודדת לפי task_id (בתוך tasks של המשתמש)
        """
        # מוצאים את המשתמש שמכיל את המטלה
        user = await self.db.user_profiles.find_one({"tasks.task_id": task_id})
        if not user:
            return None

        # בונים את הסט לעדכון
        set_fields = {f"tasks.$.{k}": v for k, v in task_update.items()}
        set_fields["tasks.$.updated_at"] = datetime.utcnow()

        result = await self.db.user_profiles.update_one(
            {"tasks.task_id": task_id},
            {"$set": set_fields}
        )

        if result.modified_count == 0:
            return None

        # מחזירים את המטלה המעודכנת (כ־dict)
        updated_user = await self.db.user_profiles.find_one({"tasks.task_id": task_id})
        for task in updated_user["tasks"]:
            if task["task_id"] == task_id:
                return task
        return None

    async def get_task(self, task_id: str):
        """
        מחזיר מטלה בודדת לפי task_id (מתוך tasks של המשתמש)
        """
        user = await self.db.user_profiles.find_one({"tasks.task_id": task_id})
        if not user or "tasks" not in user:
            return None
        for task in user["tasks"]:
            if task["task_id"] == task_id:
                return task
        return None

    async def delete_task(self, task_id: str):
        """
        מוחק מטלה בודדת לפי task_id מתוך tasks של המשתמש
        """
        result = await self.db.user_profiles.update_one(
            {"tasks.task_id": task_id},
            {"$pull": {"tasks": {"task_id": task_id}}}
        )
        return result.modified_count > 0
    
    async def delete_user_by_id(self, user_id: str) -> str:
        """Delete a single user by user_id"""
        try:
            # Check if user exists first
            user = await self.get_user_profile(user_id)
            if not user:
                return f"User {user_id} not found"
            
            # Delete the user
            result = await self.db.user_profiles.delete_one({"user_id": user_id})
            
            if result.deleted_count > 0:
                # Remove from cache if it exists
                self._user_ids_cache.discard(user_id)
                return f"Successfully deleted user {user_id}"
            else:
                return f"Failed to delete user {user_id}"
                
        except Exception as e:
            return f"Error deleting user {user_id}: {str(e)}"

    async def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        profile_dict = await self.db.user_profiles.find_one({"email": email})
        if profile_dict:
            return UserProfile(**profile_dict)
        return None

    async def verify_password_by_email(self, email: str, password: str) -> bool:
        profile = await self.get_user_by_email(email)
        if profile:
            return verify_password(password, profile.password)
        return False