"""
Repository Manager

Provides easy access to all repositories.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.roadmap_repository import RoadmapRepository
from app.db.repositories.progress_repository import ProgressRepository
from app.db.repositories.resource_repository import ResourceRepository


class RepositoryManager:
    """Manager for all database repositories"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.users = UserRepository(db)
        self.projects = ProjectRepository(db)
        self.roadmaps = RoadmapRepository(db)
        self.progress = ProgressRepository(db)
        self.resources = ResourceRepository(db)


# Global repository manager instance
repo_manager: RepositoryManager = None


def init_repositories(db: AsyncIOMotorDatabase):
    """Initialize repository manager with database"""
    global repo_manager
    repo_manager = RepositoryManager(db)
    return repo_manager


def get_repos() -> RepositoryManager:
    """Get repository manager instance"""
    return repo_manager
