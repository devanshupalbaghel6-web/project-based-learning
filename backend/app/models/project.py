from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
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
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    screenshot_url: Optional[str] = None
    user_notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class ProjectBase(BaseModel):
    """Base project model"""
    title: str
    description: str = ""
    difficulty: str = DifficultyLevel.INTERMEDIATE
    domain: str = "general"
    estimated_duration: Optional[str] = None
    duration_weeks: Optional[int] = None
    tech_stack: List[str] = Field(default_factory=list)
    skills_to_learn: List[str] = Field(default_factory=list)
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    roadmap: List[str] = Field(default_factory=list)
    checkpoints: List[Dict[str, Any]] = Field(default_factory=list)
    source: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Project creation model"""
    pass


class Project(ProjectBase):
    """Project response model"""
    id: str = Field(alias="_id")
    user_id: str
    status: str = ProjectStatus.NOT_STARTED
    progress: int = 0
    progress_percentage: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        from_attributes = True


class ProjectUpdate(BaseModel):
    """Project update model"""
    status: Optional[str] = None
    progress: Optional[int] = None
    progress_percentage: Optional[float] = None
    checkpoints: Optional[List[Dict[str, Any]]] = None
