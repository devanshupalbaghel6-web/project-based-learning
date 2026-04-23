"""
Quick data audit for MongoDB + Qdrant.

Usage:
  cd backend && source venv/bin/activate && python scripts/audit_data_state.py
"""

from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.models import Filter
from urllib.parse import urlparse, urlunparse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.core.config import settings


def normalize_qdrant_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.port is not None:
        return url
    return urlunparse(parsed._replace(netloc=f"{parsed.hostname}:6333"))


def audit_mongo() -> None:
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    collections = db.list_collection_names()
    print({"mongo_db": settings.DATABASE_NAME, "collections": collections})
    for name in collections:
        count = db[name].count_documents({})
        print({"collection": name, "count": count})


def audit_qdrant() -> None:
    if not settings.QDRANT_URL or not settings.QDRANT_API_KEY:
        print({"qdrant": "not_configured"})
        return
    client = QdrantClient(
        url=normalize_qdrant_url(settings.QDRANT_URL),
        api_key=settings.QDRANT_API_KEY,
    )
    collections = client.get_collections().collections
    names = [c.name for c in collections]
    print({"qdrant_collections": names})
    for name in names:
        info = client.count(name, count_filter=Filter(), exact=False)
        print(
            {
                "collection": name,
                "points_count_estimate": info.count,
            }
        )


if __name__ == "__main__":
    audit_mongo()
    try:
        audit_qdrant()
    except Exception as exc:
        print({"qdrant_error": str(exc)})

