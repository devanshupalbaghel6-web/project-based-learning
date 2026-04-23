from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import Resource, ResourceQuery
from app.services.orchestrator import orchestrator
from app.api.dependencies.auth import get_current_user_id
from app.db.repositories import get_repos

router = APIRouter()


@router.post("/search")
async def search_resources(
    query: ResourceQuery,
    user_id: str = Depends(get_current_user_id)
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
        "interests": [],
        "user_id": user_id,
    }
    
    user = await repos.users.find_by_id(user_id)
    if user:
        user_profile = {
            "experience_level": user.get("experience_level", "intermediate"),
            "skills": user.get("skills", user.get("current_skills", [])),
            "interests": user.get("interests", []),
            "user_id": user_id,
        }
    
    # Determine which sources to search
    sources = []
    if query.platforms:
        sources = [str(src).lower() for src in query.platforms]
    else:
        sources = ["github", "youtube", "reddit", "stackoverflow", "google"]
    
    # Aggregate resources using orchestrator
    resources = await orchestrator.aggregate_resources(
        query=query.query,
        user_profile=user_profile,
        sources=sources
    )

    # Persist discovered resources for user history/personalization and return IDs.
    persisted_resources = []
    for item in resources:
        try:
            resource_id = await repos.resources.upsert_resource(
                resource=item,
                user_id=user_id,
                saved=False,
                search_query=query.query,
            )
            persisted_resources.append({
                **item,
                "_id": resource_id,
                "platform": item.get("platform") or item.get("source", "other"),
            })
        except ValueError:
            persisted_resources.append(item)
    
    return {
        "total": len(persisted_resources),
        "resources": persisted_resources,
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
        "skills": user.get("skills", user.get("current_skills", [])),
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
            resource_id = await repos.resources.upsert_resource(
                resource=resource,
                user_id=user_id,
                saved=False,
                search_query=resource.get("title") or url,
            )
            unique_resources.append({
                **resource,
                "_id": resource_id,
                "platform": resource.get("platform") or resource.get("source", "other"),
            })
    
    return {
        "total": len(unique_resources),
        "resources": unique_resources[:10],  # Top 10 recommendations
        "reason": "Based on your current projects and learning goals"
    }


@router.get("/saved", response_model=List[Resource])
async def get_saved_resources(
    user_id: str = Depends(get_current_user_id),
    skip: int = 0,
    limit: int = 20,
    platform: str = None,
):
    """Get user's saved resources"""
    repos = get_repos()
    resources = await repos.resources.find_saved_by_user(
        user_id=user_id,
        skip=skip,
        limit=limit,
        platform=platform,
    )
    return [Resource(**item) for item in resources]


@router.get("/recent-queries")
async def get_recent_queries(
    user_id: str = Depends(get_current_user_id),
    limit: int = 5,
):
    """Get recent user search queries from persisted resource history."""
    repos = get_repos()
    queries = await repos.resources.get_recent_queries(user_id=user_id, limit=limit)
    return {"queries": queries}


@router.post("/{resource_id}/save")
async def save_resource(
    resource_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Save a resource for later"""
    repos = get_repos()

    resource = await repos.resources.find_by_id(resource_id, user_id=user_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    saved = await repos.resources.set_saved_status(resource_id, user_id, True)
    if not saved:
        raise HTTPException(status_code=500, detail="Failed to save resource")

    return {"status": "saved", "resource_id": resource_id}


@router.delete("/{resource_id}/save")
async def unsave_resource(
    resource_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Remove a resource from saved list"""
    repos = get_repos()
    success = await repos.resources.set_saved_status(resource_id, user_id, False)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")

    return {"status": "unsaved", "resource_id": resource_id}


@router.get("/platforms/{platform}")
async def get_resources_by_platform(
    platform: str,
    skip: int = 0,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get resources filtered by platform.
    
    Platforms: github, youtube, reddit, stackoverflow, google
    """
    repos = get_repos()

    # First return previously discovered resources from DB for this user.
    stored_resources = await repos.resources.list_by_user_and_platform(
        user_id=user_id,
        platform=platform,
        skip=skip,
        limit=limit,
    )

    if stored_resources:
        return {
            "platform": platform,
            "total": len(stored_resources),
            "resources": stored_resources,
        }

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
    
    # Personalized fallback query based on user profile when no stored resources exist.
    user = await repos.users.find_by_id(user_id)
    interests = user.get("interests", []) if user else []
    skills = user.get("skills", user.get("current_skills", [])) if user else []
    query_seed = " ".join((interests + skills)[:3]).strip() or "programming tutorials"

    results = await search_methods[platform](query_seed, limit)

    persisted_results = []
    for item in results:
        try:
            resource_id = await repos.resources.upsert_resource(
                resource=item,
                user_id=user_id,
                saved=False,
                search_query=query_seed,
            )
            persisted_results.append({
                **item,
                "_id": resource_id,
                "platform": item.get("platform") or item.get("source", "other"),
            })
        except ValueError:
            persisted_results.append(item)
    
    return {
        "platform": platform,
        "total": len(persisted_results),
        "resources": persisted_results,
    }
