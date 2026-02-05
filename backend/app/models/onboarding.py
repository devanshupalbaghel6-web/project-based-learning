from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class OnboardingQuestion(BaseModel):
    """Onboarding question model"""
    question: str
    options: Optional[List[str]] = None
    question_type: str  # "multiple_choice", "text", "rating"


class OnboardingResponse(BaseModel):
    """User's onboarding response"""
    question: str
    answer: str


class OnboardingData(BaseModel):
    """Complete onboarding data"""
    user_id: str
    responses: List[OnboardingResponse]
    experience_level: str
    primary_goal: str
    interests: List[str]
    completed_at: datetime
    
    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.utcnow()


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    """Chat response model"""
    message: str
    next_question: Optional[OnboardingQuestion] = None
    is_complete: bool = False
