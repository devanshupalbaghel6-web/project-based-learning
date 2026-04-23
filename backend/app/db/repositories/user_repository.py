"""
User Repository

Handles all database operations for users.
"""

from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import COLLECTIONS


class UserRepository:
    """Repository for user-related database operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[COLLECTIONS["users"]]
    
    async def create(self, user_data: Dict) -> str:
        """Create a new user"""
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    async def find_by_id(self, user_id: str) -> Optional[Dict]:
        """Find user by ID"""
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])
            return user
        except:
            return None
    
    async def find_by_email(self, email: str) -> Optional[Dict]:
        """Find user by email"""
        user = await self.collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user
    
    async def update(self, user_id: str, update_data: Dict) -> bool:
        """Update user data"""
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0 or result.matched_count > 0
    
    async def update_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Update user profile (from onboarding)"""
        profile_data["updated_at"] = datetime.utcnow()
        profile_data["onboarding_completed"] = True
        
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": profile_data}
        )
        return result.modified_count > 0 or result.matched_count > 0
    
    async def delete(self, user_id: str) -> bool:
        """Delete user"""
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """List all users with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        
        for user in users:
            user["_id"] = str(user["_id"])
        
        return users
    
    async def save_onboarding_data(self, user_id: str, onboarding_data: Dict) -> bool:
        """Save onboarding conversation and extracted data"""
        data = {
            "user_id": user_id,
            **onboarding_data,
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        # Keep one authoritative onboarding document per user.
        await self.db[COLLECTIONS["onboarding"]].update_one(
            {"user_id": user_id},
            {"$set": data, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True,
        )
        
        # Update user profile with extracted information
        profile_update = {
            "experience_level": onboarding_data.get("experience_level"),
            "interests": onboarding_data.get("interests", []),
            "skills": onboarding_data.get("current_skills", []),
            "primary_goal": onboarding_data.get("primary_goal"),
            "time_commitment": onboarding_data.get("time_commitment"),
            "onboarding_completed": True,
            "updated_at": datetime.utcnow()
        }
        
        return await self.update(user_id, profile_update)
