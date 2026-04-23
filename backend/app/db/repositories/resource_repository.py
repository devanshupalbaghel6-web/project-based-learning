"""
Resource Repository

Handles persistence for scraped and saved learning resources.
"""

from datetime import datetime
from typing import Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongodb import COLLECTIONS


class ResourceRepository:
    """Repository for resource-related database operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[COLLECTIONS["resources"]]

    @staticmethod
    def _normalize_platform(resource: Dict) -> str:
        platform = resource.get("platform") or resource.get("source") or "other"
        return str(platform).lower()

    async def upsert_resource(
        self,
        resource: Dict,
        user_id: Optional[str],
        saved: bool = False,
        search_query: Optional[str] = None,
    ) -> str:
        """Insert or update a resource by URL for a user."""
        url = (resource or {}).get("url", "").strip()
        if not url:
            raise ValueError("Resource URL is required")

        now = datetime.utcnow()
        query = {"user_id": user_id, "url": url}

        update_payload = {
            "title": resource.get("title", ""),
            "description": resource.get("description", ""),
            "url": url,
            "platform": self._normalize_platform(resource),
            "source": resource.get("source") or resource.get("platform", "other"),
            "type": resource.get("type", "resource"),
            "tags": resource.get("tags", []),
            "skills": resource.get("skills", []),
            "difficulty": resource.get("difficulty"),
            "relevance_score": float(resource.get("relevance_score", 0.0) or 0.0),
            "search_query": search_query,
            "updated_at": now,
        }

        await self.collection.update_one(
            query,
            {
                "$set": update_payload,
                "$setOnInsert": {
                    "created_at": now,
                    "saved": saved,
                    "user_id": user_id,
                },
            },
            upsert=True,
        )

        if saved:
            await self.collection.update_one(
                query,
                {"$set": {"saved": True, "updated_at": now}},
            )

        doc = await self.collection.find_one(query)
        return str(doc["_id"])

    async def upsert_many(
        self,
        resources: List[Dict],
        user_id: Optional[str],
        search_query: Optional[str] = None,
    ) -> List[str]:
        """Persist multiple resources and return their IDs."""
        ids: List[str] = []
        for item in resources:
            try:
                resource_id = await self.upsert_resource(
                    resource=item,
                    user_id=user_id,
                    saved=False,
                    search_query=search_query,
                )
                ids.append(resource_id)
            except ValueError:
                # Ignore invalid resources that have no URL.
                continue
        return ids

    async def find_saved_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        platform: Optional[str] = None,
    ) -> List[Dict]:
        """Return saved resources for a user."""
        query: Dict = {"user_id": user_id, "saved": True}
        if platform and platform.lower() != "all":
            query["platform"] = platform.lower()

        cursor = (
            self.collection.find(query)
            .sort("updated_at", -1)
            .skip(skip)
            .limit(limit)
        )
        resources = await cursor.to_list(length=limit)

        for item in resources:
            item["_id"] = str(item["_id"])

        return resources

    async def list_by_user_and_platform(
        self,
        user_id: str,
        platform: str,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict]:
        """Return previously discovered resources by platform for a user."""
        query: Dict = {"user_id": user_id}
        if platform.lower() != "all":
            query["platform"] = platform.lower()

        cursor = (
            self.collection.find(query)
            .sort("updated_at", -1)
            .skip(skip)
            .limit(limit)
        )
        resources = await cursor.to_list(length=limit)

        for item in resources:
            item["_id"] = str(item["_id"])

        return resources

    async def find_by_id(self, resource_id: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """Find a resource by ID, optionally constrained to a user."""
        try:
            query: Dict = {"_id": ObjectId(resource_id)}
        except Exception:
            return None

        if user_id is not None:
            query["user_id"] = user_id

        item = await self.collection.find_one(query)
        if item:
            item["_id"] = str(item["_id"])
        return item

    async def set_saved_status(self, resource_id: str, user_id: str, saved: bool) -> bool:
        """Set saved status for a user-owned resource."""
        try:
            object_id = ObjectId(resource_id)
        except Exception:
            return False

        result = await self.collection.update_one(
            {"_id": object_id, "user_id": user_id},
            {"$set": {"saved": saved, "updated_at": datetime.utcnow()}},
        )
        return result.modified_count > 0 or result.matched_count > 0

    async def get_recent_queries(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent search queries for a user."""
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "search_query": {"$exists": True, "$ne": None, "$ne": ""},
                }
            },
            {
                "$group": {
                    "_id": "$search_query",
                    "last_used_at": {"$max": "$updated_at"},
                }
            },
            {"$sort": {"last_used_at": -1}},
            {"$limit": limit},
        ]

        rows = await self.collection.aggregate(pipeline).to_list(length=limit)
        return [
            {
                "query": row.get("_id", ""),
                "last_used_at": row.get("last_used_at"),
            }
            for row in rows
        ]
