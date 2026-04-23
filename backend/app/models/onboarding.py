from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict, List, Optional, Literal
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
    experience_level: Literal["beginner", "intermediate", "advanced"]
    primary_goal: Literal["learn", "portfolio", "career", "exploration"]
    interests: List[str] = Field(default_factory=list)
    current_skills: List[str] = Field(default_factory=list)
    time_commitment: Optional[str] = None
    preferred_learning_style: Optional[str] = None

    @field_validator("interests", "current_skills")
    @classmethod
    def _clean_string_list(cls, value: List[str]) -> List[str]:
        cleaned = []
        for item in value or []:
            normalized = str(item).strip().lower()
            if normalized and normalized not in cleaned:
                cleaned.append(normalized)
        return cleaned[:20]

    @field_validator("time_commitment")
    @classmethod
    def _normalize_time_commitment(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return value
        return " ".join(str(value).strip().split())
    
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
