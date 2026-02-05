from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Project difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ProjectStatus(str, Enum):
    """Project status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"


class Checkpoint(BaseModel):
    """Project checkpoint model"""
    id: int
    title: str
    description: str
    completed: bool = False
    screenshot_url: Optional[str] = None
    user_notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class ProjectBase(BaseModel):
    """Base project model"""
    title: str
    description: str
    difficulty: DifficultyLevel
    domain: str
    duration_weeks: int
    tech_stack: List[str]
    resources: List[Dict[str, str]]
    roadmap: List[str]
    checkpoints: List[Checkpoint]


class ProjectCreate(ProjectBase):
    """Project creation model"""
    pass


class Project(ProjectBase):
    """Project response model"""
    id: str = Field(alias="_id")
    user_id: str
    status: ProjectStatus = ProjectStatus.NOT_STARTED
    progress: int = 0
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        from_attributes = True


class ProjectUpdate(BaseModel):
    """Project update model"""
    status: Optional[ProjectStatus] = None
    progress: Optional[int] = None
    checkpoints: Optional[List[Checkpoint]] = None
