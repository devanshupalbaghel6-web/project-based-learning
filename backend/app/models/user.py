from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user model"""
    email: str
    full_name: str


class UserCreate(UserBase):
    """User creation model"""
    password: str


class UserInDB(UserBase):
    """User in database model"""
    id: str = Field(alias="_id")
    hashed_password: str
    created_at: datetime
    onboarding_completed: bool = False
    
    class Config:
        populate_by_name = True


class User(UserBase):
    """User response model"""
    id: str
    created_at: datetime
    onboarding_completed: bool
    
    class Config:
        from_attributes = True
