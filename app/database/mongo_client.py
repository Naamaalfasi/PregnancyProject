from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MongoDBClient:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(settings.MONGO_URI)
            self.db = self.client[settings.MONGO_DB]
            # Test connection
            self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a collection from the database"""
        return self.db[collection_name]
    
    async def health_check(self) -> bool:
        """Check if MongoDB is healthy"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

# Global MongoDB client instance
mongo_client = MongoDBClient()