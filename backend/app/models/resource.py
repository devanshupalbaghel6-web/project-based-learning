from pydantic import BaseModel, Field
from typing import List, Optional
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
    description: str = ""
    url: str
    platform: str = ResourcePlatform.OTHER
    source: Optional[str] = None
    type: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    difficulty: Optional[str] = None
    relevance_score: float = 0.0


class ResourceCreate(ResourceBase):
    """Resource creation model"""
    pass


class Resource(ResourceBase):
    """Resource response model"""
    id: str = Field(alias="_id")
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    saved: bool = False
    search_query: Optional[str] = None
    
    class Config:
        populate_by_name = True
        from_attributes = True


class ResourceQuery(BaseModel):
    """Resource search query model"""
    query: str
    topics: List[str] = Field(default_factory=list)
    difficulty: Optional[str] = None
    platforms: Optional[List[str]] = None
    limit: int = 20
