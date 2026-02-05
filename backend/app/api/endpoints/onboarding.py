from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import ChatRequest, ChatResponse, OnboardingData
from app.services.orchestrator import orchestrator
from app.api.dependencies.auth import get_current_user_id, get_optional_user_id
from app.db.repositories import get_repos
from app.utils.response_parser import response_parser

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def onboarding_chat(
    request: ChatRequest,
    user_id: str = Depends(get_optional_user_id)
):
    """
    Handle onboarding chat conversation with LLM.
    
    Uses orchestrator to manage conversation flow and extract user profile.
    """
    # Use authenticated user ID if available, otherwise use from request or generate temp
    if not user_id:
        user_id = request.user_id or f"temp_{request.message[:8]}"
    
    # Process message through orchestrator
    result = await orchestrator.process_onboarding_message(
        user_id=user_id,
        message=request.message,
        context=request.context or {}
    )
    
    # If onboarding complete and user is authenticated, save profile
    if result.get("is_complete") and user_id.startswith("temp_") is False:
        repos = get_repos()
        
        # Extract and save user profile
        extracted_info = result.get("extracted_info", {})
        if extracted_info:
            await repos.users.save_onboarding_data(user_id, extracted_info)
    
    return ChatResponse(
        message=result.get("response", ""),
        is_complete=result.get("is_complete", False),
        extracted_info=result.get("extracted_info", {})
    )


@router.post("/complete", response_model=OnboardingData)
async def complete_onboarding(
    data: OnboardingData,
    user_id: str = Depends(get_current_user_id)
):
    """
    Complete onboarding and save user preferences.
    
    Triggers project recommendations and roadmap generation.
    """
    repos = get_repos()
    
    # Save onboarding data to database
    onboarding_dict = {
        "experience_level": data.experience_level,
        "interests": data.interests,
        "current_skills": data.current_skills or [],
        "primary_goal": data.primary_goal,
        "time_commitment": data.time_commitment,
        "preferred_learning_style": data.preferred_learning_style
    }
    
    await repos.users.save_onboarding_data(user_id, onboarding_dict)
    
    # Generate initial project recommendations
    user_profile = {
        "experience_level": data.experience_level,
        "interests": data.interests,
        "skills": data.current_skills or [],
        "primary_goal": data.primary_goal,
        "time_commitment": data.time_commitment
    }
    
    projects = await orchestrator.generate_personalized_projects(
        user_profile=user_profile,
        count=5
    )
    
    # Save generated projects to database
    for project_raw in projects:
        # Parse LLM response if needed
        if isinstance(project_raw, dict) and "raw_response" in project_raw:
            parsed_projects = response_parser.parse_projects_list(project_raw["raw_response"])
            
            for proj_data in parsed_projects:
                proj_data["user_id"] = user_id
                proj_data["source"] = "ai_generated"
                await repos.projects.create(proj_data)
        elif isinstance(project_raw, dict):
            project_raw["user_id"] = user_id
            project_raw["source"] = "ai_generated"
            await repos.projects.create(project_raw)
    
    return data


@router.get("/questions")
async def get_initial_questions():
    """
    Get initial onboarding questions.
    
    Returns the first set of questions for the onboarding process.
    """
    # TODO: Return dynamic initial questions based on user type
    
    return {
        "questions": [
            {
                "question": "What is your primary goal for this month?",
                "options": [
                    "Learn a new skill",
                    "Build a portfolio project",
                    "Upskill for my job",
                    "Explore a new field"
                ],
                "question_type": "multiple_choice"
            }
        ]
    }
