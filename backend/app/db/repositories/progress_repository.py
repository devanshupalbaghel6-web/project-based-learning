"""
Progress Repository

Handles all database operations for progress tracking.
"""

from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import COLLECTIONS


class ProgressRepository:
    """Repository for progress tracking database operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[COLLECTIONS["progress"]]
    
    async def create_entry(self, progress_data: Dict) -> str:
        """Create a progress entry"""
        progress_data = dict(progress_data)

        # Backward compatibility for old payloads that used `activity_type`.
        if "action" not in progress_data and "activity_type" in progress_data:
            progress_data["action"] = progress_data["activity_type"]

        progress_data["timestamp"] = progress_data.get("timestamp") or datetime.utcnow()
        
        result = await self.collection.insert_one(progress_data)
        return str(result.inserted_id)
    
    async def find_by_roadmap(
        self,
        roadmap_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """Find all progress entries for a roadmap"""
        cursor = self.collection.find(
            {"roadmap_id": roadmap_id}
        ).sort("timestamp", -1).skip(skip).limit(limit)
        
        entries = await cursor.to_list(length=limit)
        
        for entry in entries:
            entry["_id"] = str(entry["_id"])
        
        return entries
    
    async def find_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """Find all progress entries for a user"""
        cursor = self.collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).skip(skip).limit(limit)
        
        entries = await cursor.to_list(length=limit)
        
        for entry in entries:
            entry["_id"] = str(entry["_id"])
        
        return entries
    
    async def find_recent_activity(
        self,
        user_id: str,
        days: int = 7,
        limit: int = 20
    ) -> List[Dict]:
        """Find recent activity for a user"""
        from datetime import timedelta
        
        since = datetime.utcnow() - timedelta(days=days)
        
        cursor = self.collection.find({
            "user_id": user_id,
            "timestamp": {"$gte": since}
        }).sort("timestamp", -1).limit(limit)
        
        entries = await cursor.to_list(length=limit)
        
        for entry in entries:
            entry["_id"] = str(entry["_id"])
        
        return entries
    
    async def calculate_streak(self, user_id: str, roadmap_id: Optional[str] = None) -> int:
        """Calculate user's streak (consecutive days of activity)"""
        from datetime import timedelta
        
        today = datetime.utcnow().date()
        streak = 0
        current_date = today
        
        while True:
            # Check if user had activity on current_date
            start_of_day = datetime.combine(current_date, datetime.min.time())
            end_of_day = datetime.combine(current_date, datetime.max.time())
            
            day_query = {
                "user_id": user_id,
                "timestamp": {
                    "$gte": start_of_day,
                    "$lte": end_of_day
                }
            }
            if roadmap_id:
                day_query["roadmap_id"] = roadmap_id

            count = await self.collection.count_documents(day_query)
            
            if count > 0:
                streak += 1
                current_date = current_date - timedelta(days=1)
            else:
                break
            
            # Safety limit
            if streak > 365:
                break
        
        return streak
    
    async def get_stats_by_roadmap(self, roadmap_id: str) -> Dict:
        """Get statistics for a roadmap"""
        milestones_collection = self.db[COLLECTIONS["milestones"]]
        checkpoints_collection = self.db[COLLECTIONS["checkpoints"]]

        milestones = await milestones_collection.find({"roadmap_id": roadmap_id}).to_list(length=500)
        milestone_ids = [str(item["_id"]) for item in milestones]

        total_milestones = len(milestones)
        completed_milestones = sum(1 for item in milestones if item.get("status") == "completed")

        total_checkpoints = 0
        completed_checkpoints = 0
        if milestone_ids:
            total_checkpoints = await checkpoints_collection.count_documents({
                "milestone_id": {"$in": milestone_ids}
            })
            completed_checkpoints = await checkpoints_collection.count_documents({
                "milestone_id": {"$in": milestone_ids},
                "is_completed": True,
            })

        pipeline = [
            {"$match": {"roadmap_id": roadmap_id}},
            {
                "$group": {
                    "_id": "$action",
                    "count": {"$sum": 1},
                }
            },
        ]

        activity_rows = await self.collection.aggregate(pipeline).to_list(length=100)
        activity_counts = {row.get("_id", "unknown"): row.get("count", 0) for row in activity_rows}

        return {
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones,
            "total_checkpoints": total_checkpoints,
            "completed_checkpoints": completed_checkpoints,
            "activity_counts": activity_counts,
        }
