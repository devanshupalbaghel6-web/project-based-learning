"""
Reset MongoDB + Qdrant data to start fresh.

Usage:
  cd backend && source venv/bin/activate && python scripts/reset_all_user_data.py
"""

from pathlib import Path
import sys

from pymongo import MongoClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.services.qdrant_service import qdrant_service


MONGO_COLLECTIONS_TO_CLEAR = [
    "users",
    "onboarding_data",
    "projects",
    "roadmaps",
    "milestones",
    "checkpoints",
    "progress_entries",
    "resources",
]


def reset_mongo() -> None:
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    for name in MONGO_COLLECTIONS_TO_CLEAR:
        result = db[name].delete_many({})
        print({"mongo_collection": name, "deleted": result.deleted_count})


def reset_qdrant() -> None:
    ok = qdrant_service.clear_collection()
    print({"qdrant_collection": settings.QDRANT_COLLECTION, "cleared": bool(ok)})


if __name__ == "__main__":
    reset_mongo()
    reset_qdrant()

