import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.models import UserProfile, MedicalDocument, Task, DocumentType
from app.database.mongo_client import MongoDBClient
from app.database.file_processing import DocumentStatus
from app.database.data_processing import PregnancyDataProcessor
import uuid


class TestDataGenerator:
    """Generate test data for pregnancy agent application"""
    
    def __init__(self, mongo_client: MongoDBClient):
        self.mongo_client = mongo_client
        
        # Sample test data
        self.names = [
            "Sarah Johnson", "Emily Chen", "Maria Rodriguez", "Jennifer Smith", "Lisa Anderson"
        ]
        
        self.blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        
        self.common_allergies = [
            ["Penicillin", "Shellfish"], ["Latex", "Nuts"], ["Dust", "Pollen"], 
            ["Eggs", "Dairy"], ["Sulfa drugs"], []
        ]
        
        self.common_medications = [
            ["Prenatal vitamins", "Folic acid"], ["Iron supplements"], 
            ["Prenatal vitamins"], ["Calcium", "Vitamin D"], []
        ]
        
        self.medical_conditions = [
            ["Gestational diabetes"], ["High blood pressure"], ["Anemia"], 
            ["Morning sickness"], []
        ]

    def _generate_date_of_birth(self) -> str:
        """Generate a realistic date of birth (age 18-45)"""
        today = datetime.now()
        age = random.randint(18, 45)
        birth_year = today.year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Safe day for all months
        
        return f"{birth_day:02d}{birth_month:02d}{birth_year}"

    def _generate_lmp_date(self) -> str:
        """Generate a realistic LMP date (0-40 weeks ago)"""
        today = datetime.now()
        weeks_ago = random.randint(0, 40)
        lmp_date = today - timedelta(weeks=weeks_ago)
        
        return f"{lmp_date.day:02d}{lmp_date.month:02d}{lmp_date.year}"

    def _generate_height_weight(self) -> tuple:
        """Generate realistic height and weight"""
        height = round(random.uniform(150, 180), 1)  # cm
        weight = round(random.uniform(50, 100), 1)   # kg
        return height, weight

    async def create_test_user_profiles(self, count: int = 5) -> List[str]:
        """Create test user profiles"""
        created_user_ids = []
        
        for i in range(count):
            # Generate unique user ID
            user_id = f"test_user_{i+1}_{uuid.uuid4().hex[:8]}"
            
            # Generate test data
            date_of_birth = self._generate_date_of_birth()
            lmp_date = self._generate_lmp_date()
            height, weight = self._generate_height_weight()
            
            # Create user profile
            profile = UserProfile(
                user_id=user_id,
                name=self.names[i],
                date_of_birth=date_of_birth,
                lmp_date=lmp_date,
                height=height,
                weight=weight,
                blood_type=random.choice(self.blood_types),
                medical_conditions=random.choice(self.medical_conditions),
                allergies=random.choice(self.common_allergies),
                medications=random.choice(self.common_medications),
                medical_documents=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            try:
                # Create the profile
                await self.mongo_client.create_user_profile(profile)
                created_user_ids.append(user_id)
                
            except Exception as e:
                print(f"❌ Failed to create user {user_id}: {str(e)}")
                raise e
        
        return created_user_ids

    async def create_test_medical_documents(self, user_ids: List[str]) -> Dict[str, List[str]]:
        """Create test medical documents for users"""
        document_templates = [
            {"type": DocumentType.BLOOD_TEST, "name": "Complete Blood Count", "summary": "Normal CBC results"},
            {"type": DocumentType.BLOOD_TEST, "name": "Glucose Test", "summary": "Blood sugar levels within normal range"},
            {"type": DocumentType.ULTRASOUND, "name": "First Trimester Scan", "summary": "Baby developing normally"},
            {"type": DocumentType.ULTRASOUND, "name": "Anatomy Scan", "summary": "All organs developing correctly"},
            {"type": DocumentType.URINE_TEST, "name": "Urinalysis", "summary": "No signs of infection"},
            {"type": DocumentType.GENETIC_TEST, "name": "NIPT Test", "summary": "Low risk genetic screening"}
        ]
        
        created_documents = {}
        
        for user_id in user_ids:
            user_documents = []
            # Create 1-3 random documents per user
            num_docs = random.randint(1, 3)
            selected_docs = random.sample(document_templates, num_docs)
            
            for doc_template in selected_docs:
                document = MedicalDocument(
                    document_id=str(uuid.uuid4()),
                    document_type=doc_template["type"],
                    upload_date=datetime.utcnow(),
                    file_name=f"{doc_template['name'].replace(' ', '_')}_{user_id}.pdf",
                    file_path=f"/app/Uploads/{user_id}/{doc_template['name'].replace(' ', '_')}.pdf",
                    file_size=random.randint(1024, 10240),  # Random file size
                    status=random.choice([DocumentStatus.UPLOADED, DocumentStatus.COMPLETED]),
                    summary=doc_template["summary"]
                )
                
                try:
                    await self.mongo_client.add_medical_document(user_id, document, {})
                    user_documents.append(document.document_id)
                    
                except Exception as e:
                    print(f"❌ Failed to create document for {user_id}: {str(e)}")
                    raise e
            
            created_documents[user_id] = user_documents
        
        return created_documents

    async def generate_complete_test_data(self, user_count: int = 5) -> Dict[str, Any]:
        """Generate complete test data set"""
        
        # Create users
        user_ids = await self.create_test_user_profiles(user_count)
        
        if not user_ids:
            raise Exception("No users were created")
        
        # Create documents
        documents = await self.create_test_medical_documents(user_ids)
        
        # Summary
        result = {
            "users_created": len(user_ids),
            "user_ids": user_ids,
            "documents_created": sum(len(doc_list) for doc_list in documents.values()),
            "documents_by_user": documents,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return result

    async def cleanup_test_data(self, user_ids: List[str]):
        """Clean up test data"""
        
        for user_id in user_ids:
            # Delete user profile (this should cascade delete tasks and documents)
            result = await self.mongo_client.db.user_profiles.delete_one({"user_id": user_id})
            if result.deleted_count > 0:
                print(f"✅ Deleted user: {user_id}")
            else:
                print(f"❌ User not found: {user_id}")
