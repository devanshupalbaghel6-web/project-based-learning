"""
Data quality migration for projects collection.

Fixes:
- Markdown artifacts in title/description (e.g., **Title:** ...)
- Normalizes difficulty/status casing
- Ensures required defaults for dynamic frontend rendering
"""

from datetime import datetime
from pathlib import Path
import sys
from pymongo import MongoClient

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.core.config import settings


def clean_text(value: str) -> str:
    text = str(value or "").strip()
    text = text.replace("**", "")
    for prefix in ("title:", "description:"):
        if text.lower().startswith(prefix):
            text = text[len(prefix):].strip()
    return " ".join(text.split())


def run() -> None:
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    collection = db["projects"]

    docs = list(collection.find({}))
    updated = 0
    for doc in docs:
        update = {}

        title = clean_text(doc.get("title", ""))
        if title and title != doc.get("title"):
            update["title"] = title

        description = clean_text(doc.get("description", ""))
        if description != (doc.get("description") or ""):
            update["description"] = description

        difficulty = str(doc.get("difficulty", "intermediate")).strip().lower()
        if difficulty not in {"beginner", "intermediate", "advanced"}:
            difficulty = "intermediate"
        if difficulty != doc.get("difficulty"):
            update["difficulty"] = difficulty

        status = str(doc.get("status", "not_started")).strip().lower()
        if status not in {"not_started", "in_progress", "completed", "paused"}:
            status = "not_started"
        if status != doc.get("status"):
            update["status"] = status

        if "progress_percentage" not in doc:
            update["progress_percentage"] = float(doc.get("progress", 0) or 0)
        if "progress" not in doc:
            update["progress"] = int(doc.get("progress_percentage", 0) or 0)

        for required_list in ("tech_stack", "skills_to_learn", "resources", "roadmap", "checkpoints"):
            if required_list not in doc or doc.get(required_list) is None:
                update[required_list] = []

        if update:
            update["updated_at"] = datetime.utcnow()
            collection.update_one({"_id": doc["_id"]}, {"$set": update})
            updated += 1

    print({"collection": "projects", "scanned": len(docs), "updated": updated})


if __name__ == "__main__":
    run()

