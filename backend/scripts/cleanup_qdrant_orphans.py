"""
Remove orphan resource vectors from Qdrant that no longer exist in Mongo resources.

Usage:
  cd backend && source venv/bin/activate && python scripts/cleanup_qdrant_orphans.py
"""

from pathlib import Path
import sys
from typing import Set, Tuple, List, Any

from pymongo import MongoClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.services.qdrant_service import qdrant_service


def _mongo_resource_keys() -> Set[Tuple[str, str]]:
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    rows = db["resources"].find({"user_id": {"$exists": True}, "url": {"$exists": True}}, {"user_id": 1, "url": 1})
    return {(str(row.get("user_id", "")).strip(), str(row.get("url", "")).strip()) for row in rows if row.get("user_id") and row.get("url")}


def _collect_orphan_ids(valid_keys: Set[Tuple[str, str]]) -> List[Any]:
    client = qdrant_service.client
    collection = qdrant_service.collection_name
    orphans: List[Any] = []
    offset = None
    query_filter = Filter(must=[FieldCondition(key="type", match=MatchValue(value="resource"))])

    while True:
        points, next_offset = client.scroll(
            collection_name=collection,
            scroll_filter=query_filter,
            with_payload=True,
            with_vectors=False,
            limit=256,
            offset=offset,
        )
        for point in points:
            payload = point.payload or {}
            key = (str(payload.get("user_id", "")).strip(), str(payload.get("url", "")).strip())
            if not key[0] or not key[1] or key not in valid_keys:
                orphans.append(point.id)
        if next_offset is None:
            break
        offset = next_offset
    return orphans


def run() -> None:
    valid_keys = _mongo_resource_keys()
    collections = qdrant_service.client.get_collections().collections
    names = {c.name for c in collections}
    if qdrant_service.collection_name not in names:
        print(
            {
                "mongo_resource_keys": len(valid_keys),
                "qdrant_orphans_deleted": 0,
                "collection": qdrant_service.collection_name,
                "note": "collection_missing",
            }
        )
        return
    orphan_ids = _collect_orphan_ids(valid_keys)
    if orphan_ids:
        qdrant_service.client.delete(collection_name=qdrant_service.collection_name, points_selector=orphan_ids)
    print(
        {
            "mongo_resource_keys": len(valid_keys),
            "qdrant_orphans_deleted": len(orphan_ids),
            "collection": qdrant_service.collection_name,
        }
    )


if __name__ == "__main__":
    run()

