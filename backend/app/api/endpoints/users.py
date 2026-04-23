from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from app.models import User, UserCreate
from app.api.dependencies.auth import get_current_user
from app.db.repositories import get_repos
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/register", response_model=User)
async def register_user(user: UserCreate):
    """Register a new user"""
    repos = get_repos()

    existing_user = await repos.users.find_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user_id = await repos.users.create(
        {
            "email": user.email,
            "name": user.full_name,
            "hashed_password": auth_service.get_password_hash(user.password),
            "is_active": True,
            "onboarding_completed": False,
        }
    )

    saved = await repos.users.find_by_id(user_id)
    return User(
        id=saved["_id"],
        email=saved["email"],
        full_name=saved.get("name") or saved.get("full_name", ""),
        created_at=saved.get("created_at", datetime.utcnow()),
        onboarding_completed=saved.get("onboarding_completed", False),
    )


@router.get("/me", response_model=User)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return User(
        id=current_user["_id"],
        email=current_user["email"],
        full_name=current_user.get("name") or current_user.get("full_name", ""),
        created_at=current_user.get("created_at", datetime.utcnow()),
        onboarding_completed=current_user.get("onboarding_completed", False),
    )


@router.put("/me", response_model=User)
async def update_user_profile(
    updates: dict,
    current_user: dict = Depends(get_current_user),
):
    """Update current user profile"""
    repos = get_repos()

    blocked = {"email", "password", "hashed_password", "_id", "id"}
    safe_updates = {k: v for k, v in updates.items() if k not in blocked}

    if "full_name" in safe_updates:
        safe_updates["name"] = safe_updates.pop("full_name")

    success = await repos.users.update(current_user["_id"], safe_updates)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    refreshed = await repos.users.find_by_id(current_user["_id"])
    return User(
        id=refreshed["_id"],
        email=refreshed["email"],
        full_name=refreshed.get("name") or refreshed.get("full_name", ""),
        created_at=refreshed.get("created_at", datetime.utcnow()),
        onboarding_completed=refreshed.get("onboarding_completed", False),
    )


@router.get("/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """Get user statistics (projects completed, streak, etc.)"""
    repos = get_repos()
    user_id = current_user["_id"]

    projects_active = await repos.projects.count_by_user(user_id, status="in_progress")
    projects_completed = await repos.projects.count_by_user(user_id, status="completed")
    roadmaps = await repos.roadmaps.find_by_user(user_id)

    avg_progress = 0.0
    if roadmaps:
        progress_values = [float(item.get("progress_percentage", 0.0) or 0.0) for item in roadmaps]
        avg_progress = sum(progress_values) / len(progress_values)

    days_streak = await repos.progress.calculate_streak(user_id)

    return {
        "projects_active": projects_active,
        "projects_completed": projects_completed,
        "days_streak": days_streak,
        "avg_progress": round(avg_progress, 2),
    }
