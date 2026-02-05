# Database and Authentication Integration

## Overview

This update completes the backend foundation by adding:
- **MongoDB** database layer with repository pattern
- **JWT authentication** with bcrypt password hashing
- **LLM response parsers** to convert AI outputs to structured data
- **Endpoint integration** connecting all APIs to the database

---

## What's New

### 1. Database Layer

#### MongoDB Connection Manager (`app/db/mongodb.py`)
- Async MongoDB client using Motor
- Connection pooling and lifecycle management
- Health checks and error handling
- 8 collections: users, projects, roadmaps, milestones, checkpoints, progress_entries, resources, onboarding_data

#### Repository Pattern
All database operations abstracted through repository classes:

**User Repository** (`app/db/repositories/user_repository.py`)
- `create()` - Create new user
- `find_by_id()` - Get user by ID
- `find_by_email()` - Get user by email
- `save_onboarding_data()` - Save user preferences
- `update_profile()` - Update user details
- `delete()` - Remove user

**Project Repository** (`app/db/repositories/project_repository.py`)
- `create()` - Create new project
- `find_by_user()` - Get all user projects (with filters)
- `get_active_projects()` - Get in-progress projects
- `update_status()` - Change project status
- `update_progress()` - Update completion percentage
- `count_by_user()` - Count projects for user

**Roadmap Repository** (`app/db/repositories/roadmap_repository.py`)
- **Roadmap operations:**
  - `create()` - Create new roadmap
  - `find_by_project()` - Get roadmap for project
  - `find_by_user()` - Get all user roadmaps
  - `add_adaptation()` - Track roadmap changes
  
- **Milestone operations:**
  - `create_milestone()` - Add milestone to roadmap
  - `find_milestones_by_roadmap()` - Get all milestones
  - `update_milestone_status()` - Change milestone status
  
- **Checkpoint operations:**
  - `create_checkpoint()` - Add checkpoint to milestone
  - `find_checkpoints_by_milestone()` - Get all checkpoints
  - `submit_checkpoint()` - Submit checkpoint for review
  - `approve_checkpoint()` - Approve submission

**Progress Repository** (`app/db/repositories/progress_repository.py`)
- `create_entry()` - Log activity
- `find_by_roadmap()` - Get all activity for roadmap
- `find_recent_activity()` - Get recent activity (last N days)
- `calculate_streak()` - Calculate consecutive days of activity
- `get_stats_by_roadmap()` - Aggregate statistics

**Repository Manager** (`app/db/repositories/__init__.py`)
```python
from app.db.repositories import get_repos

repos = get_repos()
user = await repos.users.find_by_id(user_id)
projects = await repos.projects.find_by_user(user_id)
```

---

### 2. Authentication System

#### Auth Service (`app/services/auth_service.py`)
- **Password hashing:** Bcrypt with salt
- **JWT tokens:** Access tokens with configurable expiry
- **Token validation:** Decode and verify JWT signatures

```python
# Hash password
hashed = auth_service.get_password_hash("password123")

# Verify password
is_valid = auth_service.verify_password("password123", hashed)

# Create token
token = auth_service.create_access_token(user_id)

# Decode token
user_id = auth_service.decode_token(token)
```

#### Auth Dependencies (`app/api/dependencies/auth.py`)
FastAPI dependencies for protected routes:

```python
@router.get("/protected")
async def protected_endpoint(user_id: str = Depends(get_current_user_id)):
    # user_id extracted from JWT token
    pass

@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    # Full user object from database
    pass

@router.get("/optional")
async def optional_auth(user_id: str = Depends(get_optional_user_id)):
    # Works for both authenticated and anonymous users
    pass
```

#### Auth Endpoints (`app/api/endpoints/auth.py`)
- `POST /auth/register` - Register new user, returns JWT
- `POST /auth/login` - Login with email/password, returns JWT
- `GET /auth/me` - Get current user profile
- `PUT /auth/me` - Update user profile
- `POST /auth/change-password` - Change password

---

### 3. Response Parsers

**LLM Response Parser** (`app/utils/response_parser.py`)

Converts unstructured LLM text into structured Pydantic models:

```python
from app.utils.response_parser import response_parser

# Parse project recommendations
projects = response_parser.parse_projects_list(llm_response)
# Returns: [{"title": "...", "description": "...", "difficulty": "..."}]

# Parse roadmap structure
roadmap = response_parser.parse_roadmap(llm_response)
# Returns: {"milestones": [...], "description": "...", "duration": "..."}

# Parse project requirements
requirements = response_parser.parse_project_requirements(llm_response)
# Returns: {"skills": [...], "time": "...", "difficulty": "..."}

# Extract JSON from mixed text
data = response_parser.extract_json_from_response(llm_response)

# Parse skill lists
skills = response_parser.parse_skills_list("Python, JavaScript, React")
# Returns: ["Python", "JavaScript", "React"]
```

---

### 4. Updated Endpoints

#### Onboarding (`app/api/endpoints/onboarding.py`)
- ✅ Saves user profile to database
- ✅ Generates and persists initial project recommendations
- ✅ Uses auth for authenticated sessions

#### Projects (`app/api/endpoints/projects.py`)
- ✅ All CRUD operations use database
- ✅ Auth required for all endpoints
- ✅ Roadmap generation saves to database
- ✅ Checkpoint submission with AI feedback

**Key changes:**
```python
# OLD: Mock data
user_id = "user_123"  # TODO: Get from auth

# NEW: Real authentication
user_id: str = Depends(get_current_user_id)

# OLD: No persistence
projects = await orchestrator.generate_personalized_projects(...)
# TODO: Save to database

# NEW: Save to database
projects = await orchestrator.generate_personalized_projects(...)
for proj in projects:
    project_id = await repos.projects.create(proj)
```

#### Progress (`app/api/endpoints/progress.py`)
- ✅ Progress tracking with database
- ✅ Streak calculation
- ✅ Roadmap statistics
- ✅ Milestone and checkpoint management

#### Resources (`app/api/endpoints/resources.py`)
- ✅ Personalized search using user profile
- ✅ Recommendations based on active projects
- ✅ Optional authentication (public + private)

---

## Application Lifecycle

### Startup (`app/main.py`)
```python
@app.on_event("startup")
async def startup_event():
    # 1. Connect to MongoDB
    await mongodb.connect()
    
    # 2. Initialize repositories
    await init_repositories(mongodb.db)
    
    logging.info("✓ MongoDB connected, repositories initialized")

@app.on_event("shutdown")
async def shutdown_event():
    # Close MongoDB connection
    await mongodb.close()
```

---

## Environment Variables

Add to `.env`:

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=project_learning_platform

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

---

## Testing

### Run Integration Test

```bash
cd backend
python test_db_integration.py
```

This tests:
1. ✅ MongoDB connection
2. ✅ User creation and retrieval
3. ✅ Project CRUD operations
4. ✅ Roadmap generation
5. ✅ Milestone creation
6. ✅ Checkpoint submission
7. ✅ Progress tracking
8. ✅ Streak calculation
9. ✅ JWT authentication
10. ✅ Token generation and validation

### Manual API Testing

1. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Register a user:**
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "password123",
       "name": "John Doe"
     }'
   ```

3. **Login:**
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "password123"
     }'
   ```

4. **Use token for protected endpoints:**
   ```bash
   curl -X GET http://localhost:8000/projects/ \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
   ```

---

## Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│  (app/main.py)                         │
└───────────────┬─────────────────────────┘
                │
                ├─── Auth Middleware
                │    └─── JWT Token Validation
                │
                ├─── API Endpoints
                │    ├── /auth/* (register, login)
                │    ├── /onboarding/* (chat, complete)
                │    ├── /projects/* (CRUD, roadmaps)
                │    ├── /progress/* (tracking, stats)
                │    └── /resources/* (search, recommendations)
                │
                ├─── Services Layer
                │    ├── AuthService (JWT, bcrypt)
                │    ├── Orchestrator (LLM coordination)
                │    ├── LLMService (Gemini, Groq)
                │    ├── ScraperService (multi-platform)
                │    └── ProgressService (analytics)
                │
                ├─── Response Parsers
                │    └── LLM text → structured models
                │
                └─── Database Layer
                     ├── MongoDB (Motor async driver)
                     └── Repositories
                          ├── UserRepository
                          ├── ProjectRepository
                          ├── RoadmapRepository
                          └── ProgressRepository
```

---

## Next Steps

### Completed ✅
- MongoDB integration with repository pattern
- JWT authentication system
- All endpoints connected to database
- LLM response parsing
- Progress tracking and analytics

### Pending ⚠️
1. **Error Handling**
   - Add try-catch blocks for database operations
   - Proper HTTP status codes (404, 400, 500)
   - Input validation improvements

2. **Redis Caching** (Optional)
   - Cache common LLM responses
   - Cache resource search results
   - Session management

3. **Database Indexes**
   - Add indexes for frequently queried fields
   - Optimize query performance

4. **Integration Tests**
   - End-to-end API tests
   - Authentication flow tests
   - Roadmap generation tests

5. **Frontend Integration**
   - Connect React frontend to new endpoints
   - Implement JWT token storage
   - Add authentication context

---

## Migration from Previous Version

### Before (Mock Data):
```python
# Hardcoded user
user_id = "user_123"

# No persistence
projects = await orchestrator.generate_personalized_projects(...)
# TODO: Save to database
```

### After (Database):
```python
# Authenticated user
user_id: str = Depends(get_current_user_id)

# Persisted to database
projects = await orchestrator.generate_personalized_projects(...)
for proj in projects:
    parsed = response_parser.parse_projects_list(proj)
    await repos.projects.create(parsed)
```

---

## API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Security Notes

1. **JWT_SECRET_KEY:** Change in production! Use a strong random key:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

2. **Password Hashing:** Uses bcrypt with auto-generated salt

3. **Token Expiry:** Default 24 hours, configurable via env

4. **CORS:** Configure allowed origins in production

5. **HTTPS:** Use HTTPS in production for secure token transmission

---

## Support

For issues or questions:
1. Check MongoDB connection in `.env`
2. Verify all packages installed: `pip install -r requirements.txt`
3. Run integration test: `python test_db_integration.py`
4. Check logs for detailed error messages
