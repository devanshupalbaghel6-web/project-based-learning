import unittest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user_id, get_optional_user_id
from app.api.endpoints import progress as progress_endpoint
from app.api.endpoints import projects as projects_endpoint
from app.api.endpoints import resources as resources_endpoint


class FakeResourceRepo:
    def __init__(self):
        self.resources = {}
        self.counter = 1

    async def upsert_resource(self, resource, user_id, saved=False, search_query=None):
        resource_id = f"res_{self.counter}"
        self.counter += 1
        doc = {
            "_id": resource_id,
            "user_id": user_id,
            "saved": saved,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "search_query": search_query,
            "platform": (resource.get("platform") or resource.get("source") or "other").lower(),
            **resource,
        }
        self.resources[resource_id] = doc
        return resource_id

    async def find_by_id(self, resource_id, user_id=None):
        doc = self.resources.get(resource_id)
        if not doc:
            return None
        if user_id is not None and doc.get("user_id") != user_id:
            return None
        return {**doc}

    async def set_saved_status(self, resource_id, user_id, saved):
        doc = self.resources.get(resource_id)
        if not doc or doc.get("user_id") != user_id:
            return False
        doc["saved"] = saved
        doc["updated_at"] = datetime.utcnow()
        return True

    async def find_saved_by_user(self, user_id, skip=0, limit=20, platform=None):
        rows = [
            {**item}
            for item in self.resources.values()
            if item.get("user_id") == user_id and item.get("saved")
        ]
        if platform:
            rows = [item for item in rows if item.get("platform") == platform.lower()]
        return rows[skip : skip + limit]

    async def list_by_user_and_platform(self, user_id, platform, skip=0, limit=20):
        rows = [
            {**item}
            for item in self.resources.values()
            if item.get("user_id") == user_id
        ]
        if platform.lower() != "all":
            rows = [item for item in rows if item.get("platform") == platform.lower()]
        return rows[skip : skip + limit]

    async def get_recent_queries(self, user_id, limit=5):
        rows = []
        seen = set()
        for item in sorted(self.resources.values(), key=lambda r: r.get("updated_at", datetime.min), reverse=True):
            if item.get("user_id") != user_id:
                continue
            query = item.get("search_query")
            if not query or query in seen:
                continue
            seen.add(query)
            rows.append({"query": query, "last_used_at": item.get("updated_at")})
            if len(rows) >= limit:
                break
        return rows


class FakeUsersRepo:
    async def find_by_id(self, user_id):
        return {
            "_id": user_id,
            "name": "Test User",
            "email": "test@example.com",
            "experience_level": "intermediate",
            "skills": ["Python"],
            "interests": ["ai"],
        }


class FakeProjectsRepo:
    def __init__(self):
        self.projects = {
            "proj_1": {
                "_id": "proj_1",
                "user_id": "user_1",
                "title": "Scoped Project",
                "description": "Project description",
                "difficulty": "intermediate",
                "domain": "ai",
                "tech_stack": ["Python", "FastAPI"],
                "resources": [],
                "roadmap": [],
                "checkpoints": [],
                "status": "in_progress",
                "progress": 40,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        }

    async def get_active_projects(self, user_id):
        return [item for item in self.projects.values() if item.get("user_id") == user_id and item.get("status") == "in_progress"]

    async def find_by_id(self, project_id):
        return self.projects.get(project_id)


class FakeRoadmapsRepoForProjects:
    async def find_by_project(self, project_id):
        return {
            "_id": "roadmap_1",
            "project_id": project_id,
            "user_id": "user_1",
            "title": "Existing roadmap",
            "description": "already there",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

    async def find_milestones_by_roadmap(self, roadmap_id):
        return []

    async def find_checkpoints_by_milestone(self, milestone_id):
        return []


class FakeProgressRepo:
    def __init__(self):
        self.created_entries = []

    async def create_entry(self, payload):
        self.created_entries.append(payload)
        return f"pe_{len(self.created_entries)}"


class FakeRoadmapsRepoForProgress:
    async def find_checkpoint_by_id(self, checkpoint_id):
        return {"_id": checkpoint_id, "milestone_id": "milestone_1", "is_completed": False}

    async def find_milestone_by_id(self, milestone_id):
        return {"_id": milestone_id, "roadmap_id": "roadmap_1"}

    async def find_by_id(self, roadmap_id):
        return {"_id": roadmap_id, "user_id": "user_1", "project_id": "proj_1"}

    async def update_checkpoint(self, checkpoint_id, update_data):
        return True

    async def find_checkpoints_by_milestone(self, milestone_id):
        return [
            {"_id": "cp_1", "is_completed": True},
            {"_id": "cp_2", "is_completed": True},
        ]

    async def update_milestone_status(self, milestone_id, status):
        return True


class ApiScopingTests(unittest.TestCase):
    def test_resource_search_and_save_flow(self):
        app = FastAPI()
        app.include_router(resources_endpoint.router, prefix="/resources")
        app.dependency_overrides[get_optional_user_id] = lambda: "user_1"
        app.dependency_overrides[get_current_user_id] = lambda: "user_1"

        fake_repos = type("Repos", (), {
            "resources": FakeResourceRepo(),
            "users": FakeUsersRepo(),
            "projects": FakeProjectsRepo(),
        })()

        sample_resources = [
            {
                "title": "FastAPI Tutorial",
                "description": "Learn API design",
                "url": "https://example.com/fastapi",
                "source": "github",
                "type": "tutorial",
            }
        ]

        with patch.object(resources_endpoint, "get_repos", return_value=fake_repos), patch.object(
            resources_endpoint.orchestrator,
            "aggregate_resources",
            new=AsyncMock(return_value=sample_resources),
        ):
            client = TestClient(app)

            search_response = client.post("/resources/search", json={"query": "fastapi", "platforms": ["github"], "limit": 5})
            self.assertEqual(search_response.status_code, 200)
            payload = search_response.json()
            self.assertEqual(payload["total"], 1)
            self.assertIn("_id", payload["resources"][0])

            resource_id = payload["resources"][0]["_id"]

            save_response = client.post(f"/resources/{resource_id}/save")
            self.assertEqual(save_response.status_code, 200)
            self.assertEqual(save_response.json()["status"], "saved")

            saved_response = client.get("/resources/saved")
            self.assertEqual(saved_response.status_code, 200)
            saved_items = saved_response.json()
            self.assertEqual(len(saved_items), 1)
            self.assertEqual(saved_items[0]["_id"], resource_id)

    def test_existing_project_roadmap_returns_without_generation(self):
        app = FastAPI()
        app.include_router(projects_endpoint.router, prefix="/projects")
        app.dependency_overrides[get_current_user_id] = lambda: "user_1"

        fake_repos = type("Repos", (), {
            "projects": FakeProjectsRepo(),
            "roadmaps": FakeRoadmapsRepoForProjects(),
            "users": FakeUsersRepo(),
        })()

        with patch.object(projects_endpoint, "get_repos", return_value=fake_repos):
            client = TestClient(app)
            response = client.get("/projects/proj_1/roadmap")

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["_id"], "roadmap_1")
            self.assertEqual(payload["project_id"], "proj_1")
            self.assertIn("milestones", payload)

    def test_progress_endpoint_records_action_field(self):
        app = FastAPI()
        app.include_router(progress_endpoint.router, prefix="/progress")
        app.dependency_overrides[get_current_user_id] = lambda: "user_1"

        progress_repo = FakeProgressRepo()
        fake_repos = type("Repos", (), {
            "progress": progress_repo,
            "roadmaps": FakeRoadmapsRepoForProgress(),
        })()

        with patch.object(progress_endpoint, "get_repos", return_value=fake_repos):
            client = TestClient(app)
            response = client.post("/progress/checkpoints/checkpoint_1/complete")

            self.assertEqual(response.status_code, 200)
            self.assertTrue(progress_repo.created_entries)
            self.assertTrue(all("action" in entry for entry in progress_repo.created_entries))


if __name__ == "__main__":
    unittest.main()
