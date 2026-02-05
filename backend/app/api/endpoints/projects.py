from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.models import Project, ProjectCreate, ProjectUpdate
from app.services.orchestrator import orchestrator
from app.services.scraper_service import scraper_service
from app.models.progress import Roadmap
from app.api.dependencies.auth import get_current_user_id
from app.db.repositories import get_repos
from app.utils.response_parser import response_parser
from datetime import datetime
from app.services.llm_service import llm_service
from app.services.progress_service import progress_service

router = APIRouter()


@router.get("/", response_model=List[Project])
async def get_projects(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all projects for the current user
    
    Can be filtered by status (not_started, in_progress, completed)
    """
    repos = get_repos()
    
    # Query projects from database with filtering
    projects = await repos.projects.find_by_user(
        user_id=user_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return [Project(**proj) for proj in projects]


@router.get("/recommended", response_model=List[Project])
async def get_recommended_projects(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get AI-recommended projects based on user profile.
    
    Uses onboarding data and orchestrator to generate personalized projects
    combining LLM generation and web scraping.
    """
    repos = get_repos()
    
    # Fetch user profile from database
    user = await repos.users.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    user_profile = {
        "experience_level": user.get("experience_level", "beginner"),
        "interests": user.get("interests", []),
        "skills": user.get("current_skills", []),
        "primary_goal": user.get("primary_goal", "learning")
    }
    
    # Generate personalized projects using orchestrator
    projects_raw = await orchestrator.generate_personalized_projects(
        user_profile=user_profile,
        count=5
    )
    
    # Parse and save generated projects
    recommended_projects = []
    for project_raw in projects_raw:
        # Parse LLM response if needed
        if isinstance(project_raw, dict) and "raw_response" in project_raw:
            parsed_projects = response_parser.parse_projects_list(project_raw["raw_response"])
            
            for proj_data in parsed_projects:
                proj_data["user_id"] = user_id
                proj_data["source"] = "ai_generated"
                proj_data["status"] = "not_started"
                proj_data["created_at"] = datetime.utcnow()
                proj_data["updated_at"] = datetime.utcnow()
                
                project_id = await repos.projects.create(proj_data)
                saved_project = await repos.projects.find_by_id(project_id)
                recommended_projects.append(Project(**saved_project))
        elif isinstance(project_raw, dict):
            project_raw["user_id"] = user_id
            project_raw["source"] = "ai_generated"
            project_raw["status"] = "not_started"
            project_raw["created_at"] = datetime.utcnow()
            project_raw["updated_at"] = datetime.utcnow()
            
            project_id = await repos.projects.create(project_raw)
            saved_project = await repos.projects.find_by_id(project_id)
            recommended_projects.append(Project(**saved_project))
    
    return recommended_projects


@router.post("/generate")
async def generate_project(
    prompt: str,
    user_level: str = "intermediate",
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate a custom project based on user prompt.
    
    Uses LLM to create complete project structure with roadmap.
    """
    repos = get_repos()
    
    # Generate project using LLM
    project_data = await llm_service.generate_custom_project(
        prompt=prompt,
        user_level=user_level
    )
    
    # Parse structured data from LLM response
    if "raw_response" in project_data:
        parsed_projects = response_parser.parse_projects_list(project_data["raw_response"])
        
        if parsed_projects:
            # Take first generated project
            proj = parsed_projects[0]
            proj["user_id"] = user_id
            proj["source"] = "ai_generated"
            proj["status"] = "not_started"
            proj["created_at"] = datetime.utcnow()
            proj["updated_at"] = datetime.utcnow()
            
            # Save to database
            project_id = await repos.projects.create(proj)
            saved_project = await repos.projects.find_by_id(project_id)
            
            return {
                "status": "success",
                "project": Project(**saved_project),
                "message": "Project generated successfully"
            }
    
    return {
        "status": "error",
        "message": "Failed to generate project"
    }


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific project by ID"""
    repos = get_repos()
    
    # Query project from database
    project = await repos.projects.find_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify user has access to this project
    if project.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    return Project(**project)


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    update: ProjectUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Update project progress, status, or checkpoints
    """
    repos = get_repos()
    
    # Get project from database
    project = await repos.projects.find_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify user has access
    if project.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update project fields
    update_data = update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    success = await repos.projects.update(project_id, update_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update project")
    
    # Return updated project
    updated_project = await repos.projects.find_by_id(project_id)
    return Project(**updated_project)


@router.get("/{project_id}/roadmap")
async def get_project_roadmap(
    project_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get learning roadmap for a project.
    
    Returns milestones, checkpoints, and resources.
    """
    repos = get_repos()
    
    # Fetch project from database
    project = await repos.projects.find_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify access
    if project.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if roadmap already exists
    existing_roadmaps = await repos.roadmaps.find_by_project(project_id)
    
    if existing_roadmaps:
        # Return existing roadmap with milestones
        roadmap = existing_roadmaps[0]
        roadmap_id = roadmap["_id"]
        
        # Fetch milestones
        milestones = await repos.roadmaps.find_milestones_by_roadmap(roadmap_id)
        
        # Fetch checkpoints for each milestone
        for milestone in milestones:
            milestone_id = milestone["_id"]
            checkpoints = await repos.roadmaps.find_checkpoints_by_milestone(milestone_id)
            milestone["checkpoints"] = checkpoints
        
        roadmap["milestones"] = milestones
        return roadmap
    
    # Generate new roadmap if none exists
    user = await repos.users.find_by_id(user_id)
    user_profile = {
        "experience_level": user.get("experience_level", "beginner"),
        "skills": user.get("current_skills", [])
    }
    
    # Generate roadmap using orchestrator
    roadmap_result = await orchestrator.generate_dynamic_roadmap(
        user_id=user_id,
        project=project,
        user_profile=user_profile
    )
    
    # Parse and save roadmap
    if roadmap_result and "raw_response" in roadmap_result:
        parsed_roadmap = response_parser.parse_roadmap(roadmap_result["raw_response"])
        
        # Create roadmap in database
        roadmap_dict = {
            "project_id": project_id,
            "user_id": user_id,
            "title": f"Roadmap for {project.get('title')}",
            "description": parsed_roadmap.get("description", ""),
            "estimated_duration": parsed_roadmap.get("estimated_duration"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_adaptive": True,
            "adaptation_count": 0
        }
        
        roadmap_id = await repos.roadmaps.create(roadmap_dict)
        
        # Create milestones and checkpoints
        for milestone_data in parsed_roadmap.get("milestones", []):
            milestone_dict = {
                "roadmap_id": roadmap_id,
                "title": milestone_data.get("title"),
                "description": milestone_data.get("description"),
                "order": milestone_data.get("order", 0),
                "estimated_duration": milestone_data.get("estimated_duration"),
                "status": "not_started"
            }
            
            milestone_id = await repos.roadmaps.create_milestone(milestone_dict)
            
            # Create checkpoints
            for checkpoint_data in milestone_data.get("checkpoints", []):
                checkpoint_dict = {
                    "milestone_id": milestone_id,
                    "title": checkpoint_data.get("title"),
                    "description": checkpoint_data.get("description"),
                    "order": checkpoint_data.get("order", 0),
                    "is_completed": False,
                    "submission_required": checkpoint_data.get("submission_required", False)
                }
                
                await repos.roadmaps.create_checkpoint(checkpoint_dict)
        
        # Fetch and return complete roadmap
        saved_roadmap = await repos.roadmaps.find_by_id(roadmap_id)
        milestones = await repos.roadmaps.find_milestones_by_roadmap(roadmap_id)
        
        for milestone in milestones:
            milestone_id = milestone["_id"]
            checkpoints = await repos.roadmaps.find_checkpoints_by_milestone(milestone_id)
            milestone["checkpoints"] = checkpoints
        
        saved_roadmap["milestones"] = milestones
        return saved_roadmap
    
    raise HTTPException(status_code=500, detail="Failed to generate roadmap")


@router.post("/{project_id}/checkpoints/{checkpoint_id}/submit")
async def submit_checkpoint(
    project_id: str,
    checkpoint_id: str,
    screenshot_url: str,
    notes: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Submit a checkpoint with screenshot and notes for AI analysis
    """
    repos = get_repos()
    
    # Fetch checkpoint from database
    checkpoint = await repos.roadmaps.find_checkpoint_by_id(checkpoint_id)
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    # Analyze submission with LLM
    analysis = await llm_service.analyze_checkpoint_submission(
        checkpoint=checkpoint,
        screenshot_url=screenshot_url,
        user_notes=notes
    )
    
    # Get milestone and roadmap for this checkpoint
    milestone = await repos.roadmaps.find_milestone_by_id(checkpoint["milestone_id"])
    roadmap_id = milestone["roadmap_id"]
    
    # Submit checkpoint
    submission_data = {
        "screenshot_url": screenshot_url,
        "notes": notes,
        "ai_feedback": analysis.get("feedback", ""),
        "submitted_at": datetime.utcnow()
    }
    
    success = await repos.roadmaps.submit_checkpoint(checkpoint_id, submission_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to submit checkpoint")
    
    # Track progress
    await progress_service.track_checkpoint_submission(
        user_id=user_id,
        roadmap_id=str(roadmap_id),
        checkpoint_id=checkpoint_id,
        submission_data={
            "milestone_id": str(milestone["_id"]),
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
