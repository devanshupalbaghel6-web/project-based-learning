from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class ResourcePlatform(str, Enum):
    """Resource platform types"""
    GITHUB = "github"
    YOUTUBE = "youtube"
    DOCUMENTATION = "documentation"
    REDDIT = "reddit"
    STACKOVERFLOW = "stackoverflow"
    MEDIUM = "medium"
    ARXIV = "arxiv"
    OTHER = "other"


class ResourceBase(BaseModel):
    """Base resource model"""
    title: str
    description: str
    url: str
    platform: ResourcePlatform
    tags: List[str]
    relevance_score: float = 0.0


class ResourceCreate(ResourceBase):
    """Resource creation model"""
    pass


class Resource(ResourceBase):
    """Resource response model"""
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    saved: bool = False
    
    class Config:
        from_attributes = True


class ResourceQuery(BaseModel):
    """Resource search query model"""
    query: str
    platforms: Optional[List[ResourcePlatform]] = None
    limit: int = 20
