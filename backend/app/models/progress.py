"""
Roadmap and Progress Tracking Models

Models for dynamic roadmaps that adapt based on user progress.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class MilestoneStatus(str, Enum):
    """Status of a roadmap milestone"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class Milestone(BaseModel):
    """A milestone in the learning roadmap"""
    id: str
    title: str
    description: str
    duration_weeks: float
    prerequisites: List[str] = []
    skills_to_learn: List[str] = []
    resources: List[str] = []  # Resource IDs
    checkpoints: List[str] = []  # Checkpoint IDs
    status: MilestoneStatus = MilestoneStatus.NOT_STARTED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    order: int


class CheckpointStatus(str, Enum):
    """Status of a checkpoint"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"


class Checkpoint(BaseModel):
    """A practical checkpoint to verify progress"""
    id: str
    milestone_id: str
    title: str
    description: str
    deliverable: str  # What user needs to submit
    example_url: Optional[str] = None
    status: CheckpointStatus = CheckpointStatus.PENDING
    submitted_at: Optional[datetime] = None
    submission_url: Optional[str] = None  # Screenshot/demo URL
    submission_notes: Optional[str] = None
    feedback: Optional[str] = None
    approved_at: Optional[datetime] = None


class Roadmap(BaseModel):
    """Learning roadmap for a project"""
    id: str
    user_id: str
    project_id: str
    title: str
    description: Optional[str] = None
    milestones: List[Milestone] = []
    total_duration_weeks: float
    current_milestone_id: Optional[str] = None
    progress_percentage: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: Optional[datetime] = None
    is_adaptive: bool = True  # Whether roadmap adjusts based on progress
    adaptations: List[Dict] = []  # History of adaptations


class ProgressEntry(BaseModel):
    """User progress entry"""
    id: str
    user_id: str
    roadmap_id: str
    milestone_id: str
    checkpoint_id: Optional[str] = None
    action: str  # "started_milestone", "completed_checkpoint", "submitted", etc.
    metadata: Dict = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserProgress(BaseModel):
    """Aggregated user progress"""
    user_id: str
    roadmap_id: str
    milestones_completed: int = 0
    milestones_total: int = 0
    checkpoints_completed: int = 0
    checkpoints_total: int = 0
    current_milestone: Optional[str] = None
    time_spent_hours: float = 0.0
    average_pace: str = "normal"  # "slow", "normal", "fast"
    skills_acquired: List[str] = []
    struggles: List[str] = []  # Skills user is struggling with
    strengths: List[str] = []  # Skills user excels at
    last_activity: Optional[datetime] = None
    streak_days: int = 0


class ProgressAnalysis(BaseModel):
    """AI analysis of user progress"""
    user_id: str
    roadmap_id: str
    overall_performance: str  # "excellent", "good", "needs_support"
    pace_assessment: str  # "too_fast", "optimal", "too_slow"
    recommendations: List[str] = []
    struggling_areas: List[str] = []
    suggested_adjustments: Dict = {}
    next_steps: List[str] = []
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
