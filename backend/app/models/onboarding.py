from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
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
    experience_level: str
    primary_goal: str
    interests: List[str] = Field(default_factory=list)
    current_skills: List[str] = Field(default_factory=list)
    time_commitment: Optional[str] = None
    preferred_learning_style: Optional[str] = None
    
    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    user_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Chat response model"""
    message: str
    next_question: Optional[OnboardingQuestion] = None
    is_complete: bool = False
    extracted_info: Dict[str, Any] = Field(default_factory=dict)
