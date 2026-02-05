"""
Project Repository

Handles all database operations for projects.
"""

from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import COLLECTIONS


class ProjectRepository:
    """Repository for project-related database operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[COLLECTIONS["projects"]]
    
    async def create(self, project_data: Dict) -> str:
        """Create a new project"""
        project_data["created_at"] = datetime.utcnow()
        project_data["updated_at"] = datetime.utcnow()
        project_data["status"] = project_data.get("status", "not_started")
        
        result = await self.collection.insert_one(project_data)
        return str(result.inserted_id)
    
    async def find_by_id(self, project_id: str) -> Optional[Dict]:
        """Find project by ID"""
        try:
            project = await self.collection.find_one({"_id": ObjectId(project_id)})
            if project:
                project["_id"] = str(project["_id"])
            return project
        except:
            return None
    
    async def find_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Dict]:
        """Find projects by user ID with optional status filter"""
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        projects = await cursor.to_list(length=limit)
        
        for project in projects:
            project["_id"] = str(project["_id"])
        
        return projects
    
    async def update(self, project_id: str, update_data: Dict) -> bool:
        """Update project"""
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def update_status(self, project_id: str, status: str) -> bool:
        """Update project status"""
        return await self.update(project_id, {"status": status})
    
    async def update_progress(self, project_id: str, progress_percentage: float) -> bool:
        """Update project progress"""
        return await self.update(project_id, {"progress_percentage": progress_percentage})
    
    async def delete(self, project_id: str) -> bool:
        """Delete project"""
        result = await self.collection.delete_one({"_id": ObjectId(project_id)})
        return result.deleted_count > 0
    
    async def count_by_user(self, user_id: str, status: Optional[str] = None) -> int:
        """Count projects for a user"""
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        
        return await self.collection.count_documents(query)
    
    async def get_active_projects(self, user_id: str) -> List[Dict]:
        """Get user's active projects (in_progress)"""
        return await self.find_by_user(user_id, status="in_progress")
