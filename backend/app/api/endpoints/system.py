from fastapi import APIRouter, Depends
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.api.dependencies.auth import get_current_user_id
from app.db.repositories import get_repos
from app.services.qdrant_service import qdrant_service

router = APIRouter()


@router.get("/health-consistency")
async def health_consistency(user_id: str = Depends(get_current_user_id)):
    """
    One-click health + data consistency report for the authenticated user.
    Checks Mongo and Qdrant user-scoped resource/project counts and sync gap.
    """
    repos = get_repos()
    db = repos.users.collection.database

    mongo_projects = await db.projects.count_documents({"user_id": user_id})
    mongo_resources = await db.resources.count_documents({"user_id": user_id})
    mongo_saved_resources = await db.resources.count_documents({"user_id": user_id, "saved": True})
    mongo_onboarding = await db.onboarding_data.count_documents({"user_id": user_id})

    qdrant_resource_count = 0
    qdrant_ok = bool(qdrant_service.client)
    qdrant_error = None
    if qdrant_service.client:
        try:
            count_result = qdrant_service.client.count(
                collection_name=qdrant_service.collection_name,
                count_filter=Filter(
                    must=[
                        FieldCondition(key="type", match=MatchValue(value="resource")),
                        FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                    ]
                ),
                exact=False,
            )
            qdrant_resource_count = int(count_result.count or 0)
        except Exception as exc:
            qdrant_ok = False
            qdrant_error = str(exc)

    return {
        "status": "ok" if qdrant_ok else "degraded",
        "user_id": user_id,
        "mongo": {
            "projects": mongo_projects,
            "resources": mongo_resources,
            "saved_resources": mongo_saved_resources,
            "onboarding_records": mongo_onboarding,
        },
        "qdrant": {
            "collection": qdrant_service.collection_name,
            "resource_points_for_user": qdrant_resource_count,
            "ok": qdrant_ok,
            "error": qdrant_error,
        },
        "consistency": {
            "resource_gap": mongo_resources - qdrant_resource_count,
            "in_sync": mongo_resources == qdrant_resource_count and qdrant_ok,
        },
    }

