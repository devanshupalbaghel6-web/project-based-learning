from fastapi import APIRouter
from app.api.endpoints import onboarding, projects, resources, users, progress, auth, system

router = APIRouter()

# Authentication routes (no auth required)
router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# Include endpoint routers
router.include_router(
    onboarding.router,
    prefix="/onboarding",
    tags=["onboarding"]
)

router.include_router(
    projects.router,
    prefix="/projects",
    tags=["projects"]
)

router.include_router(
    resources.router,
    prefix="/resources",
    tags=["resources"]
)

router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

router.include_router(
    progress.router,
    prefix="/progress",
    tags=["progress", "roadmap"]
)

router.include_router(
    system.router,
    prefix="/system",
    tags=["system", "health"]
)
