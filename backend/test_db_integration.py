"""
Database Integration Test

Tests the complete database integration including:
- User authentication
- Project management
- Roadmap generation
- Progress tracking
"""

import asyncio
import os
from dotenv import load_dotenv
from bson import ObjectId

# Load environment variables
load_dotenv()

from app.db.mongodb import MongoDB
from app.db.repositories import init_repositories, get_repos
from app.services.auth_service import auth_service


async def test_database_integration():
    """Test complete database flow"""
    
    print("=" * 60)
    print("Database Integration Test")
    print("=" * 60)
    
    # Initialize MongoDB connection
    print("\n1. Connecting to MongoDB...")
    mongodb = MongoDB()
    await mongodb.connect()
    print("✓ Connected to MongoDB")
    
    # Initialize repositories
    print("\n2. Initializing repositories...")
    init_repositories(mongodb.db)
    repos = get_repos()
    print("✓ Repositories initialized")
    
    # Test user creation
    print("\n3. Testing user creation...")
    test_email = f"test_{asyncio.get_event_loop().time()}@example.com"
    
    user_data = {
        "email": test_email,
        "name": "Test User",
        "hashed_password": auth_service.get_password_hash("testpassword123"),
        "experience_level": "intermediate",
        "interests": ["web development", "AI"],
        "current_skills": ["Python", "JavaScript"],
        "primary_goal": "portfolio",
        "time_commitment": "10-15 hours/week",
        "preferred_learning_style": "hands_on"
    }
    
    user_id = await repos.users.create(user_data)
    print(f"✓ User created with ID: {user_id}")
    
    # Verify user retrieval
    user = await repos.users.find_by_id(user_id)
    assert user is not None
    assert user["email"] == test_email
    print(f"✓ User retrieved: {user['name']}")
    
    # Test project creation
    print("\n4. Testing project creation...")
    project_data = {
        "user_id": user_id,
        "title": "Build a Task Manager App",
        "description": "Full-stack task management application with React and FastAPI",
        "category": "web_development",
        "difficulty": "intermediate",
        "estimated_duration": "4-6 weeks",
        "skills_to_learn": ["React", "FastAPI", "PostgreSQL", "Docker"],
        "status": "in_progress",
        "source": "ai_generated",
        "progress": 0
    }
    
    project_id = await repos.projects.create(project_data)
    print(f"✓ Project created with ID: {project_id}")
    
    # Verify project retrieval
    project = await repos.projects.find_by_id(project_id)
    assert project is not None
    assert project["title"] == "Build a Task Manager App"
    print(f"✓ Project retrieved: {project['title']}")
    
    # Test roadmap creation
    print("\n5. Testing roadmap creation...")
    roadmap_data = {
        "project_id": project_id,
        "user_id": user_id,
        "title": f"Roadmap for {project['title']}",
        "description": "Step-by-step guide to building the task manager",
        "estimated_duration": "6 weeks",
        "is_adaptive": True,
        "adaptation_count": 0
    }
    
    roadmap_id = await repos.roadmaps.create(roadmap_data)
    print(f"✓ Roadmap created with ID: {roadmap_id}")
    
    # Create milestones
    print("\n6. Creating milestones...")
    milestone_1_data = {
        "roadmap_id": roadmap_id,
        "title": "Setup Development Environment",
        "description": "Install Node.js, Python, and set up the project structure",
        "order": 1,
        "estimated_duration": "3 days",
        "status": "completed"
    }
    
    milestone_1_id = await repos.roadmaps.create_milestone(milestone_1_data)
    print(f"✓ Milestone 1 created: {milestone_1_data['title']}")
    
    milestone_2_data = {
        "roadmap_id": roadmap_id,
        "title": "Build Backend API",
        "description": "Create REST API with FastAPI and database models",
        "order": 2,
        "estimated_duration": "1 week",
        "status": "in_progress"
    }
    
    milestone_2_id = await repos.roadmaps.create_milestone(milestone_2_data)
    print(f"✓ Milestone 2 created: {milestone_2_data['title']}")
    
    # Create checkpoints
    print("\n7. Creating checkpoints...")
    checkpoint_1_data = {
        "milestone_id": milestone_2_id,
        "title": "Create database schema",
        "description": "Define SQLAlchemy models for tasks, users, and projects",
        "order": 1,
        "is_completed": False,
        "submission_required": True
    }
    
    checkpoint_1_id = await repos.roadmaps.create_checkpoint(checkpoint_1_data)
    print(f"✓ Checkpoint 1 created: {checkpoint_1_data['title']}")
    
    checkpoint_2_data = {
        "milestone_id": milestone_2_id,
        "title": "Implement CRUD endpoints",
        "description": "Create endpoints for creating, reading, updating, and deleting tasks",
        "order": 2,
        "is_completed": False,
        "submission_required": True
    }
    
    checkpoint_2_id = await repos.roadmaps.create_checkpoint(checkpoint_2_data)
    print(f"✓ Checkpoint 2 created: {checkpoint_2_data['title']}")
    
    # Test checkpoint submission
    print("\n8. Testing checkpoint submission...")
    submission_data = {
        "screenshot_url": "https://example.com/screenshot.png",
        "notes": "Implemented all database models with proper relationships",
        "ai_feedback": "Great work! Your schema design looks solid."
    }
    
    success = await repos.roadmaps.submit_checkpoint(checkpoint_1_id, submission_data)
    assert success
    print(f"✓ Checkpoint submitted successfully")
    
    # Test progress tracking
    print("\n9. Testing progress tracking...")
    progress_entry = {
        "user_id": user_id,
        "roadmap_id": roadmap_id,
        "milestone_id": milestone_2_id,
        "checkpoint_id": checkpoint_1_id,
        "activity_type": "checkpoint_submitted",
        "metadata": {
            "submission_url": submission_data["screenshot_url"],
            "notes": submission_data["notes"]
        }
    }
    
    progress_id = await repos.progress.create_entry(progress_entry)
    print(f"✓ Progress entry created with ID: {progress_id}")
    
    # Test progress retrieval
    print("\n10. Testing progress retrieval...")
    recent_activity = await repos.progress.find_recent_activity(user_id, days=7)
    print(f"✓ Found {len(recent_activity)} recent activities")
    
    # Test streak calculation
    streak = await repos.progress.calculate_streak(user_id, roadmap_id)
    print(f"✓ Current streak: {streak} days")
    
    # Test roadmap stats
    stats = await repos.progress.get_stats_by_roadmap(roadmap_id)
    print(f"✓ Roadmap stats: {stats}")
    
    # Test user authentication
    print("\n11. Testing authentication...")
    
    # Verify password
    is_valid = auth_service.verify_password("testpassword123", user["hashed_password"])
    assert is_valid
    print("✓ Password verification successful")
    
    # Create JWT token
    token = auth_service.create_access_token({"sub": user_id})
    print(f"✓ JWT token created: {token[:50]}...")
    
    # Decode token
    decoded_payload = auth_service.decode_token(token)
    assert decoded_payload and decoded_payload.get("sub") == user_id
    print(f"✓ Token decoded successfully: {decoded_payload.get('sub')}")
    
    # Test fetching user projects
    print("\n12. Testing project queries...")
    user_projects = await repos.projects.find_by_user(user_id)
    print(f"✓ Found {len(user_projects)} projects for user")
    
    active_projects = await repos.projects.get_active_projects(user_id)
    print(f"✓ Found {len(active_projects)} active projects")
    
    # Test fetching roadmap with milestones
    print("\n13. Testing roadmap queries...")
    roadmap = await repos.roadmaps.find_by_id(roadmap_id)
    assert roadmap is not None
    print(f"✓ Roadmap retrieved: {roadmap['title']}")
    
    milestones = await repos.roadmaps.find_milestones_by_roadmap(roadmap_id)
    print(f"✓ Found {len(milestones)} milestones")
    
    for milestone in milestones:
        checkpoints = await repos.roadmaps.find_checkpoints_by_milestone(str(milestone["_id"]))
        print(f"  - {milestone['title']}: {len(checkpoints)} checkpoints")
    
    # Cleanup
    print("\n14. Cleaning up test data...")
    await repos.progress.collection.delete_one({"_id": ObjectId(progress_id)})
    await repos.roadmaps.checkpoints_collection.delete_many({"milestone_id": milestone_2_id})
    await repos.roadmaps.milestones_collection.delete_many({"roadmap_id": roadmap_id})
    await repos.roadmaps.collection.delete_one({"_id": ObjectId(roadmap_id)})
    await repos.projects.delete(project_id)
    await repos.users.delete(user_id)
    print("✓ Test data cleaned up")
    
    # Close connection
    print("\n15. Closing MongoDB connection...")
    await mongodb.close()
    print("✓ Connection closed")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_database_integration())
