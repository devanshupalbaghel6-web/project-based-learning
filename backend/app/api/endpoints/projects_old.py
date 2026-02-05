from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import Project, ProjectCreate, ProjectUpdate
from app.services.orchestrator import orchestrator
from app.services.scraper_service import scraper_service
from app.models.progress import Roadmap

router = APIRouter()


@router.get("/", response_model=List[Project])
async def get_projects(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
):
    """
    Get all projects for the current user
    
    Can be filtered by status (not_started, in_progress, completed)
    """
    # TODO: Get user_id from auth token
    # TODO: Query projects from database
    # TODO: Filter by status if provided
    # TODO: Implement pagination
    
    return []


@router.get("/recommended", response_model=List[Project])
async def get_recommended_projects():
    """
    Get AI-recommended projects based on user profile.
    
    Uses onboarding data and orchestrator to generate personalized projects
    combining LLM generation and web scraping.
    """
    # TODO: Get user_id from auth and fetch profile from database
    user_profile = {
        "experience_level": "intermediate",
        "interests": ["web development", "AI"],
        "skills": ["Python", "JavaScript", "React"],
        "primary_goal": "portfolio"
    }
    
    # Generate personalized projects using orchestrator
    projects = await orchestrator.generate_personalized_projects(
        user_profile=user_profile,
        count=5
    )
    
    # TODO: Save generated projects to database
    # TODO: Convert to Project model format
    
    return []


@router.post("/generate")
async def generate_project(prompt: str, user_level: str = "intermediate"):
    """
    Generate a custom project based on user prompt.
    
    Uses LLM to create complete project structure with roadmap.
    """
    from app.services.llm_service import llm_service
    
    # Generate project using LLM
    project_data = await llm_service.generate_custom_project(
        prompt=prompt,
        user_level=user_level
    )
    
    # TODO: Parse structured data from LLM response
    # TODO: Save project to database
    # TODO: Generate initial roadmap
    
    return {
        "status": "success",
        "project": project_data,
        "message": "Project generated successfully"
    }


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get a specific project by ID"""
    # TODO: Query project from database
    # TODO: Verify user has access to this project
    
    raise HTTPException(status_code=404, detail="Project not found")


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, update: ProjectUpdate):
    """
    Update project progress, status, or checkpoints
    """
    # TODO: Get project from database
    # TODO: Verify user has access
    # TODO: Update project fields
    # TODO: If checkpoint updated, use LLM to analyze progress
    # TODO: Return updated project
    
    raise HTTPException(status_code=404, detail="Project not found")


@router.get("/{project_id}/roadmap")
async def get_project_roadmap(project_id: str):
    """
    Get learning roadmap for a project.
    
    Returns milestones, checkpoints, and resources.
    """
    # TODO: Get user_id from auth
    user_id = "user_123"
    
    # TODO: Fetch project from database
    project = {
        "id": project_id,
        "title": "Build a Task Manager App",
        "description": "Create a full-stack task management application"
    }
    
    # TODO: Fetch user profile
    user_profile = {
        "experience_level": "intermediate",
        "skills": ["Python", "JavaScript"]
    }
    
    # Generate roadmap using orchestrator
    roadmap = await orchestrator.generate_dynamic_roadmap(
        user_id=user_id,
        project=project,
        user_profile=user_profile
    )
    
    # TODO: Save roadmap to database
    
    return roadmap


@router.post("/{project_id}/checkpoints/{checkpoint_id}/submit")
async def submit_checkpoint(
    project_id: str,
    checkpoint_id: str,
    screenshot_url: str,
    notes: str
):
    """
    Submit a checkpoint for review.
    
    Uses LLM to analyze submission and provide feedback.
    """
    from app.services.llm_service import llm_service
    from app.services.progress_service import progress_service
    
    # TODO: Fetch checkpoint from database
    checkpoint = {
        "id": checkpoint_id,
        "title": "Create Database Schema",
        "description": "Design and implement database models"
    }
    
    # Analyze submission with LLM
    analysis = await llm_service.analyze_checkpoint_submission(
        checkpoint=checkpoint,
        screenshot_url=screenshot_url,
        user_notes=notes
    )
    
    # Track progress
    # TODO: Get user_id and roadmap_id from database
    user_id = "user_123"
    roadmap_id = "roadmap_456"
    
    await progress_service.track_checkpoint_submission(
        user_id=user_id,
        roadmap_id=roadmap_id,
        checkpoint_id=checkpoint_id,
        submission_data={
            "milestone_id": "milestone_1",
            "screenshot_url": screenshot_url,
            "notes": notes,
            "analysis": analysis
        }
    )
    
    return {
        "status": "submitted",
        "feedback": analysis.get("feedback"),
        "approved": analysis.get("approved"),
        "suggestions": analysis.get("suggestions", [])
    }
@router.post("/{project_id}/checkpoints/{checkpoint_id}/submit")
async def submit_checkpoint(
    project_id: str,
    checkpoint_id: int,
    screenshot_url: str,
    notes: str,
):
    """
    Submit a checkpoint with screenshot and notes for AI analysis
    """
    # TODO: Get project and checkpoint
    # TODO: Store screenshot and notes
    # TODO: Use LLM to analyze submission
    # TODO: Provide feedback
    # TODO: Update checkpoint status
    
    return {
        "status": "submitted",
        "feedback": "Great work! Your implementation looks solid."
    }


@router.get("/{project_id}/roadmap")
async def get_project_roadmap(project_id: str):
    """Get detailed roadmap for a project"""
    # TODO: Get project from database
    # TODO: Return detailed roadmap with resources
    
    raise HTTPException(status_code=404, detail="Project not found")
