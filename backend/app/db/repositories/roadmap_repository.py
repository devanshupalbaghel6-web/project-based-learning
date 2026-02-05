"""
Roadmap Repository

Handles all database operations for roadmaps, milestones, and checkpoints.
"""

from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import COLLECTIONS


class RoadmapRepository:
    """Repository for roadmap-related database operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[COLLECTIONS["roadmaps"]]
        self.milestones_collection = db[COLLECTIONS["milestones"]]
        self.checkpoints_collection = db[COLLECTIONS["checkpoints"]]
    
    async def create(self, roadmap_data: Dict) -> str:
        """Create a new roadmap"""
        roadmap_data["created_at"] = datetime.utcnow()
        roadmap_data["updated_at"] = datetime.utcnow()
        roadmap_data["progress_percentage"] = 0.0
        roadmap_data["adaptations"] = []
        
        result = await self.collection.insert_one(roadmap_data)
        return str(result.inserted_id)
    
    async def find_by_id(self, roadmap_id: str) -> Optional[Dict]:
        """Find roadmap by ID"""
        try:
            roadmap = await self.collection.find_one({"_id": ObjectId(roadmap_id)})
            if roadmap:
                roadmap["_id"] = str(roadmap["_id"])
            return roadmap
        except:
            return None
    
    async def find_by_project(self, project_id: str) -> Optional[Dict]:
        """Find roadmap by project ID"""
        roadmap = await self.collection.find_one({"project_id": project_id})
        if roadmap:
            roadmap["_id"] = str(roadmap["_id"])
        return roadmap
    
    async def find_by_user(self, user_id: str) -> List[Dict]:
        """Find all roadmaps for a user"""
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        roadmaps = await cursor.to_list(length=100)
        
        for roadmap in roadmaps:
            roadmap["_id"] = str(roadmap["_id"])
        
        return roadmaps
    
    async def update(self, roadmap_id: str, update_data: Dict) -> bool:
        """Update roadmap"""
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(roadmap_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def add_adaptation(self, roadmap_id: str, adaptation: Dict) -> bool:
        """Add an adaptation record to roadmap"""
        adaptation["timestamp"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(roadmap_id)},
            {
                "$push": {"adaptations": adaptation},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    async def update_progress(self, roadmap_id: str, progress_percentage: float) -> bool:
        """Update roadmap progress"""
        return await self.update(roadmap_id, {
            "progress_percentage": progress_percentage,
            "last_activity_at": datetime.utcnow()
        })
    
    async def update_current_milestone(self, roadmap_id: str, milestone_id: str) -> bool:
        """Update current active milestone"""
        return await self.update(roadmap_id, {"current_milestone_id": milestone_id})
    
    # Milestone operations
    
    async def create_milestone(self, milestone_data: Dict) -> str:
        """Create a new milestone"""
        milestone_data["created_at"] = datetime.utcnow()
        milestone_data["status"] = milestone_data.get("status", "not_started")
        
        result = await self.milestones_collection.insert_one(milestone_data)
        return str(result.inserted_id)
    
    async def find_milestone_by_id(self, milestone_id: str) -> Optional[Dict]:
        """Find milestone by ID"""
        try:
            milestone = await self.milestones_collection.find_one({"_id": ObjectId(milestone_id)})
            if milestone:
                milestone["_id"] = str(milestone["_id"])
            return milestone
        except:
            return None
    
    async def find_milestones_by_roadmap(self, roadmap_id: str) -> List[Dict]:
        """Find all milestones for a roadmap"""
        cursor = self.milestones_collection.find({"roadmap_id": roadmap_id}).sort("order", 1)
        milestones = await cursor.to_list(length=100)
        
        for milestone in milestones:
            milestone["_id"] = str(milestone["_id"])
        
        return milestones
    
    async def update_milestone(self, milestone_id: str, update_data: Dict) -> bool:
        """Update milestone"""
        result = await self.milestones_collection.update_one(
            {"_id": ObjectId(milestone_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def update_milestone_status(self, milestone_id: str, status: str) -> bool:
        """Update milestone status"""
        update_data = {"status": status}
        
        if status == "in_progress":
            update_data["started_at"] = datetime.utcnow()
        elif status == "completed":
            update_data["completed_at"] = datetime.utcnow()
        
        return await self.update_milestone(milestone_id, update_data)
    
    # Checkpoint operations
    
    async def create_checkpoint(self, checkpoint_data: Dict) -> str:
        """Create a new checkpoint"""
        checkpoint_data["created_at"] = datetime.utcnow()
        checkpoint_data["status"] = checkpoint_data.get("status", "pending")
        
        result = await self.checkpoints_collection.insert_one(checkpoint_data)
        return str(result.inserted_id)
    
    async def find_checkpoint_by_id(self, checkpoint_id: str) -> Optional[Dict]:
        """Find checkpoint by ID"""
        try:
            checkpoint = await self.checkpoints_collection.find_one({"_id": ObjectId(checkpoint_id)})
            if checkpoint:
                checkpoint["_id"] = str(checkpoint["_id"])
            return checkpoint
        except:
            return None
    
    async def find_checkpoints_by_milestone(self, milestone_id: str) -> List[Dict]:
        """Find all checkpoints for a milestone"""
        cursor = self.checkpoints_collection.find({"milestone_id": milestone_id})
        checkpoints = await cursor.to_list(length=100)
        
        for checkpoint in checkpoints:
            checkpoint["_id"] = str(checkpoint["_id"])
        
        return checkpoints
    
    async def update_checkpoint(self, checkpoint_id: str, update_data: Dict) -> bool:
        """Update checkpoint"""
        result = await self.checkpoints_collection.update_one(
            {"_id": ObjectId(checkpoint_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def submit_checkpoint(
        self,
        checkpoint_id: str,
        submission_data: Dict
    ) -> bool:
        """Submit checkpoint for review"""
        update_data = {
            "status": "submitted",
            "submitted_at": datetime.utcnow(),
            **submission_data
        }
        
        return await self.update_checkpoint(checkpoint_id, update_data)
    
    async def approve_checkpoint(self, checkpoint_id: str, feedback: str) -> bool:
        """Approve checkpoint submission"""
        return await self.update_checkpoint(checkpoint_id, {
            "status": "approved",
            "approved_at": datetime.utcnow(),
            "feedback": feedback
        })
    
    async def request_revision(self, checkpoint_id: str, feedback: str) -> bool:
        """Request revision on checkpoint"""
        return await self.update_checkpoint(checkpoint_id, {
            "status": "needs_revision",
            "feedback": feedback
        })
