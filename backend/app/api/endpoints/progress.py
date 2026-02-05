"""
Progress and Roadmap API Endpoints

Endpoints for tracking user progress and managing dynamic roadmaps.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.models.progress import (
    Roadmap, Milestone, Checkpoint, UserProgress, ProgressAnalysis
)
from app.services.progress_service import progress_service
from app.services.orchestrator import orchestrator
from app.api.dependencies.auth import get_current_user_id
from app.db.repositories import get_repos
from app.utils.response_parser import response_parser
from datetime import datetime

router = APIRouter()


@router.get("/roadmap/{roadmap_id}")
async def get_roadmap(
    roadmap_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get roadmap details including milestones and checkpoints.
    """
    repos = get_repos()
    
    # Fetch roadmap from database
    roadmap = await repos.roadmaps.find_by_id(roadmap_id)
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    # Verify user access
    if roadmap.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this roadmap")
    
    # Fetch milestones and checkpoints
    milestones = await repos.roadmaps.find_milestones_by_roadmap(roadmap_id)
    
    for milestone in milestones:
        milestone_id = milestone["_id"]
        checkpoints = await repos.roadmaps.find_checkpoints_by_milestone(milestone_id)
        milestone["checkpoints"] = checkpoints
    
    roadmap["milestones"] = milestones
    
    return roadmap


@router.post("/roadmap/generate")
async def generate_roadmap(
    project_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate a new roadmap for a project.
    
    Creates milestones, checkpoints, and finds relevant resources.
    """
    repos = get_repos()
    
    # Fetch project from database
    project = await repos.projects.find_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify access
    if project.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Fetch user profile
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
        
        # Fetch complete roadmap
        saved_roadmap = await repos.roadmaps.find_by_id(roadmap_id)
        milestones = await repos.roadmaps.find_milestones_by_roadmap(roadmap_id)
        
        for milestone in milestones:
            milestone_id = milestone["_id"]
            checkpoints = await repos.roadmaps.find_checkpoints_by_milestone(milestone_id)
            milestone["checkpoints"] = checkpoints
        
        saved_roadmap["milestones"] = milestones
        
        return {
            "status": "success",
            "roadmap": saved_roadmap,
            "message": "Roadmap generated successfully"
        }
    
    raise HTTPException(status_code=500, detail="Failed to generate roadmap")


@router.get("/progress/{roadmap_id}")
async def get_progress(
    roadmap_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get user's progress on a roadmap.
    
    Returns completion stats, current milestone, and analytics.
    """
    repos = get_repos()
    
    # Verify roadmap exists and belongs to user
    roadmap = await repos.roadmaps.find_by_id(roadmap_id)
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    if roadmap.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Calculate progress using service
    progress = await progress_service.calculate_user_progress(
        user_id=user_id,
        roadmap_id=roadmap_id
    )
    
    # Fetch progress entries from database
    progress_entries = await repos.progress.find_by_roadmap(roadmap_id)
    
    # Calculate streak
    streak = await repos.progress.calculate_streak(user_id, roadmap_id)
    
    # Get roadmap stats
    stats = await repos.progress.get_stats_by_roadmap(roadmap_id)
    
    return {
        **progress,
        "progress_entries": progress_entries,
        "current_streak": streak,
        "stats": stats
    }


@router.get("/progress/{roadmap_id}/analysis")
async def analyze_progress(
    roadmap_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get AI analysis of user's progress.
    
    Provides recommendations, identifies struggles, and suggests adjustments.
    """
    repos = get_repos()
    
    # Verify access
    roadmap = await repos.roadmaps.find_by_id(roadmap_id)
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    if roadmap.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Analyze progress
    analysis = await progress_service.analyze_progress(
        user_id=user_id,
        roadmap_id=roadmap_id
    )
    
    return analysis


@router.post("/checkpoints/{checkpoint_id}/complete")
async def complete_checkpoint(
    checkpoint_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Mark a checkpoint as completed.
    
    Updates progress and may trigger roadmap adaptation.
    """
    repos = get_repos()
    
    # Fetch checkpoint
    checkpoint = await repos.roadmaps.find_checkpoint_by_id(checkpoint_id)
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    # Get milestone and roadmap
    milestone = await repos.roadmaps.find_milestone_by_id(checkpoint["milestone_id"])
    roadmap = await repos.roadmaps.find_by_id(milestone["roadmap_id"])
    
    # Verify access
    if roadmap.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Mark checkpoint as complete
    update_data = {
        "is_completed": True,
        "completed_at": datetime.utcnow()
    }
    
    success = await repos.roadmaps.update_checkpoint(checkpoint_id, update_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to complete checkpoint")
    
    # Track progress
    await repos.progress.create_entry({
        "user_id": user_id,
        "roadmap_id": str(milestone["roadmap_id"]),
        "milestone_id": str(checkpoint["milestone_id"]),
        "checkpoint_id": checkpoint_id,
        "activity_type": "checkpoint_completed",
        "timestamp": datetime.utcnow()
    })
    
    # Check if all checkpoints in milestone are complete
    all_checkpoints = await repos.roadmaps.find_checkpoints_by_milestone(checkpoint["milestone_id"])
    all_complete = all(cp.get("is_completed", False) for cp in all_checkpoints)
    
    if all_complete:
        # Mark milestone as complete
        await repos.roadmaps.update_milestone_status(checkpoint["milestone_id"], "completed")
        
        # Track milestone completion
        await repos.progress.create_entry({
            "user_id": user_id,
            "roadmap_id": str(milestone["roadmap_id"]),
            "milestone_id": str(checkpoint["milestone_id"]),
            "activity_type": "milestone_completed",
            "timestamp": datetime.utcnow()
        })
    
    return {
        "status": "success",
        "checkpoint_id": checkpoint_id,
        "milestone_complete": all_complete
    }


@router.get("/milestones/{milestone_id}")
async def get_milestone(
    milestone_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get milestone details with checkpoints.
    """
    repos = get_repos()
    
    # Fetch milestone
    milestone = await repos.roadmaps.find_milestone_by_id(milestone_id)
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    # Verify access via roadmap
    roadmap = await repos.roadmaps.find_by_id(milestone["roadmap_id"])
    
    if roadmap.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Fetch checkpoints
    checkpoints = await repos.roadmaps.find_checkpoints_by_milestone(milestone_id)
    milestone["checkpoints"] = checkpoints
    
    return milestone


@router.post("/roadmap/{roadmap_id}/adapt")
async def adapt_roadmap(
    roadmap_id: str,
    reason: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Trigger roadmap adaptation based on user progress or difficulties.
    
    AI analyzes current progress and adjusts roadmap accordingly.
    """
    repos = get_repos()
    
    # Verify access
    roadmap = await repos.roadmaps.find_by_id(roadmap_id)
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    if roadmap.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Request adaptation from orchestrator
    adapted_roadmap = await orchestrator.adapt_roadmap(
        roadmap_id=roadmap_id,
        user_id=user_id,
        reason=reason
    )
    
    # Track adaptation
    adaptation_data = {
        "timestamp": datetime.utcnow(),
        "reason": reason,
        "changes": adapted_roadmap.get("changes", [])
    }
    
    await repos.roadmaps.add_adaptation(roadmap_id, adaptation_data)
    
    return {
        "status": "success",
        "message": "Roadmap adapted successfully",
        "changes": adapted_roadmap.get("changes", [])
    }


@router.get("/activity/recent")
async def get_recent_activity(
    user_id: str = Depends(get_current_user_id),
    days: int = Query(7, ge=1, le=30)
):
    """
    Get recent activity for user across all roadmaps.
    """
    repos = get_repos()
    
    # Fetch recent activity
    activities = await repos.progress.find_recent_activity(user_id, days=days)
    
    return {
        "activities": activities,
        "period_days": days
    }


@router.get("/stats")
async def get_user_stats(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get overall user statistics across all projects and roadmaps.
    """
    repos = get_repos()
    
    # Get all user roadmaps
    roadmaps = await repos.roadmaps.find_by_user(user_id)
    
    # Calculate aggregate stats
    total_checkpoints = 0
    completed_checkpoints = 0
    total_milestones = 0
    completed_milestones = 0
    
    for roadmap in roadmaps:
        roadmap_id = roadmap["_id"]
        stats = await repos.progress.get_stats_by_roadmap(str(roadmap_id))
        
        total_checkpoints += stats.get("total_checkpoints", 0)
        completed_checkpoints += stats.get("completed_checkpoints", 0)
        total_milestones += stats.get("total_milestones", 0)
        completed_milestones += stats.get("completed_milestones", 0)
    
    # Calculate longest streak across all roadmaps
    max_streak = 0
    for roadmap in roadmaps:
        roadmap_id = str(roadmap["_id"])
        streak = await repos.progress.calculate_streak(user_id, roadmap_id)
        max_streak = max(max_streak, streak)
    
    return {
        "total_projects": len(roadmaps),
        "total_milestones": total_milestones,
        "completed_milestones": completed_milestones,
        "total_checkpoints": total_checkpoints,
        "completed_checkpoints": completed_checkpoints,
        "completion_rate": completed_checkpoints / total_checkpoints if total_checkpoints > 0 else 0,
        "longest_streak": max_streak
    }
