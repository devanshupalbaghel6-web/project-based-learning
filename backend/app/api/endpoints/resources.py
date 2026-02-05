from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import Resource, ResourceQuery
from app.services.orchestrator import orchestrator
from app.api.dependencies.auth import get_current_user_id, get_optional_user_id
from app.db.repositories import get_repos

router = APIRouter()


@router.post("/search")
async def search_resources(
    query: ResourceQuery,
    user_id: str = Depends(get_optional_user_id)
):
    """
    Search for resources across multiple platforms.
    
    Scrapes GitHub, YouTube, Reddit, Stack Overflow, Google
    and returns relevant resources ranked by relevance.
    """
    repos = get_repos()
    
    # Get user profile if authenticated
    user_profile = {
        "experience_level": query.difficulty or "intermediate",
        "skills": query.topics or [],
        "interests": []
    }
    
    if user_id:
        user = await repos.users.find_by_id(user_id)
        if user:
            user_profile = {
                "experience_level": user.get("experience_level", "intermediate"),
                "skills": user.get("current_skills", []),
                "interests": user.get("interests", [])
            }
    
    # Determine which sources to search
    sources = []
    if query.platforms:
        sources = query.platforms
    else:
        sources = ["github", "youtube", "reddit", "stackoverflow", "google"]
    
    # Aggregate resources using orchestrator
    resources = await orchestrator.aggregate_resources(
        query=query.query,
        user_profile=user_profile,
        sources=sources
    )
    
    return {
        "total": len(resources),
        "resources": resources
    }


@router.get("/recommended")
async def get_recommended_resources(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get AI-recommended resources based on user's current projects and progress.
    """
    repos = get_repos()
    
    # Get user's active projects
    active_projects = await repos.projects.get_active_projects(user_id)
    
    if not active_projects:
        raise HTTPException(status_code=404, detail="No active projects found")
    
    # Get user profile
    user = await repos.users.find_by_id(user_id)
    user_profile = {
        "experience_level": user.get("experience_level", "intermediate"),
        "skills": user.get("current_skills", []),
        "interests": user.get("interests", [])
    }
    
    # Identify skills needed from active projects
    all_skills = []
    search_queries = []
    
    for project in active_projects:
        project_skills = project.get("skills_to_learn", [])
        all_skills.extend(project_skills)
        
        # Create search query for this project
        search_queries.append(
            f"{project.get('title')} {' '.join(project_skills[:3])}"
        )
    
    # Search for resources relevant to current learning goals
    all_resources = []
    
    for search_query in search_queries[:2]:  # Limit to 2 projects to avoid too many requests
        resources = await orchestrator.aggregate_resources(
            query=search_query,
            user_profile=user_profile,
            sources=["youtube", "github", "google"]
        )
        all_resources.extend(resources)
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_resources = []
    for resource in all_resources:
        url = resource.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_resources.append(resource)
    
    return {
        "total": len(unique_resources),
        "resources": unique_resources[:10],  # Top 10 recommendations
        "reason": "Based on your current projects and learning goals"
    }


@router.get("/saved", response_model=List[Resource])
async def get_saved_resources():
    """Get user's saved resources"""
    # TODO: Query saved resources from database
    # TODO: Return user's saved resources
    
    return []


@router.post("/{resource_id}/save")
async def save_resource(resource_id: str):
    """Save a resource for later"""
    # TODO: Add resource to user's saved list in database
    
    return {"status": "saved"}


@router.delete("/{resource_id}/save")
async def unsave_resource(resource_id: str):
    """Remove a resource from saved list"""
    # TODO: Remove resource from user's saved list
    
    return {"status": "unsaved"}


@router.get("/platforms/{platform}")
async def get_resources_by_platform(
    platform: str,
    skip: int = 0,
    limit: int = 20,
):
    """
    Get resources filtered by platform.
    
    Platforms: github, youtube, reddit, stackoverflow, google
    """
    # TODO: Query resources by platform from database or scrape fresh
    
    from app.services.scraper_service import scraper_service
    
    # Map platform to scraper method
    search_methods = {
        "github": scraper_service.search_github,
        "youtube": scraper_service.search_youtube,
        "reddit": scraper_service.search_reddit,
        "stackoverflow": scraper_service.search_stackoverflow,
        "google": scraper_service.search_google
    }
    
    if platform not in search_methods:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {platform}")
    
    # Generic search for platform
    # TODO: Get search query from user preferences or trending topics
    results = await search_methods[platform]("programming tutorials", limit)
    
    return {
        "platform": platform,
        "total": len(results),
        "resources": results
    }
