"""
MongoDB Database Connection and Operations

Handles MongoDB connection, database operations, and provides
helper functions for CRUD operations.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.DATABASE_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            # Do not raise here to allow the application to start in
            # development environments where MongoDB may be unreachable.
            self.client = None
            self.db = None
            return
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def get_collection(self, name: str):
        """Get a collection from database"""
        if not self.db:
            raise RuntimeError("Database not connected")
        return self.db[name]


# Global MongoDB instance
mongodb = MongoDB()


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance"""
    return mongodb.db


# Collection names
COLLECTIONS = {
    "users": "users",
    "projects": "projects",
    "roadmaps": "roadmaps",
    "resources": "resources",
    "progress": "progress_entries",
    "checkpoints": "checkpoints",
    "milestones": "milestones",
    "onboarding": "onboarding_data"
}
