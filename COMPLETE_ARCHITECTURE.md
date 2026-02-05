# Complete System Architecture & Flow

## Overview

This platform provides a **one-stop solution** for project-based learning by intelligently connecting **Projects**, **Roadmaps**, and **Resources** through AI orchestration.

## 🎯 Core Philosophy

The platform operates on three interconnected pillars:
1. **Projects**: What you want to build
2. **Roadmaps**: How to build it (adaptive learning path)
3. **Resources**: Where to learn (curated from web)

Everything is contextually linked through AI-powered RAG (Retrieval Augmented Generation).

---

## 🏗️ System Architecture

### Component Layers

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  Onboarding → Dashboard → Projects → Roadmaps → Resources   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│     /onboarding  /projects  /resources  /progress           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator Service                       │
│        (Coordinates all AI services and workflows)           │
└─────────────────────────────────────────────────────────────┘
         ↓              ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ LLM Service  │ │ Groq Service │ │ RAG Pipeline │ │  Scraping    │
│   (Gemini)   │ │   (Llama)    │ │ (Embeddings) │ │   Service    │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
         ↓                                  ↓              ↓
┌──────────────────────────────────────────────────────────────┐
│                    Data Layer                                 │
│   MongoDB (Projects/Users)  +  Qdrant (Vector DB)            │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete User Journey

### Phase 1: Onboarding

**Objective**: Understand user profile and learning goals

```
User Input → Orchestrator.process_onboarding_message()
           → LLM Service (Gemini) generates contextual questions
           → Extract: experience_level, interests, goals, time_commitment
           → Save to MongoDB
```

**LLM Usage**: Gemini (conversational AI for natural onboarding)

**Data Flow**:
1. User sends message via `/api/onboarding/chat`
2. Orchestrator maintains conversation memory (LangChain)
3. After 3-4 exchanges, profile is complete
4. POST `/api/onboarding/complete` saves profile and triggers project generation

---

### Phase 2: Project Generation

**Objective**: Generate personalized projects (hybrid approach: both LLM + scraping)

```
User Profile → Orchestrator.generate_personalized_projects()
             ├─→ Groq: Extract key skills/interests (fast classification)
             ├─→ RAG: Search Qdrant for similar projects (local embeddings)
             ├─→ Gemini: Generate custom projects with context
             └─→ Scraper: Find real-world GitHub projects
             → Combine & rank → Save to MongoDB
```

**Smart LLM Routing**:
- **Groq (Llama)**: Quick skill extraction, classification
- **Gemini (2.5 Flash)**: Complex project generation with creative thinking

**API Endpoints**:
- `GET /api/projects/recommended` - Get AI-generated projects
- `POST /api/projects/generate` - Generate custom project from prompt

**Example Flow**:
```python
# User profile after onboarding
user_profile = {
    "experience_level": "intermediate",
    "interests": ["web development", "AI"],
    "skills": ["Python", "JavaScript"],
    "primary_goal": "portfolio"
}

# Orchestrator generates 5 projects
projects = await orchestrator.generate_personalized_projects(
    user_profile=user_profile,
    count=5
)

# Returns mix of:
# 1. LLM-generated custom projects
# 2. Scraped GitHub projects matching profile
# 3. Ranked by relevance using embeddings
```

---

### Phase 3: Dynamic Roadmap Creation

**Objective**: Create adaptive learning path with milestones and checkpoints

```
Selected Project → Orchestrator.generate_dynamic_roadmap()
                 ├─→ Groq: Parse project requirements (skills, time, difficulty)
                 ├─→ RAG: Find learning resources for each skill (Qdrant)
                 ├─→ Gemini: Generate structured roadmap with milestones
                 └─→ Create checkpoints for progress verification
                 → Save Roadmap to MongoDB
```

**Roadmap Structure**:
```
Roadmap
  ├─ Milestone 1: Setup & Basics (2 weeks)
  │   ├─ Checkpoint 1.1: Environment setup
  │   ├─ Checkpoint 1.2: Hello World
  │   └─ Resources: [YouTube tutorial, GitHub starter]
  ├─ Milestone 2: Core Features (3 weeks)
  │   ├─ Checkpoint 2.1: Database schema
  │   ├─ Checkpoint 2.2: API endpoints
  │   └─ Resources: [Stack Overflow, Official docs]
  └─ Milestone 3: Advanced Features (2 weeks)
```

**API Endpoint**:
- `GET /api/projects/{id}/roadmap` - Get/generate roadmap

---

### Phase 4: Resource Aggregation

**Objective**: Find best learning resources from multiple platforms

```
User Query → Orchestrator.aggregate_resources()
           ├─→ Groq: Generate optimized search query
           ├─→ Scraper: Parallel scraping
           │   ├─ GitHub API (repositories)
           │   ├─ YouTube API (videos)
           │   ├─ Reddit API (discussions)
           │   ├─ Stack Overflow API (Q&A)
           │   └─ Google Custom Search (articles)
           ├─→ Groq: Classify & tag each resource (type, difficulty, skills)
           ├─→ Gemini: Rank by relevance to user profile
           └─→ Store in Qdrant for future RAG
```

**Platform Integration**:

| Platform | API | Purpose | Output |
|----------|-----|---------|--------|
| GitHub | REST API | Find project examples, libraries | Repositories with stars, topics |
| YouTube | Data API v3 | Find tutorials, courses | Videos with metadata |
| Reddit | JSON API | Find discussions, tips | Posts from r/learnprogramming |
| Stack Overflow | Stack Exchange API | Find solutions to problems | Q&A with code snippets |
| Google | Custom Search API | Find articles, documentation | Web pages |

**Smart Resource Classification** (Groq):
```python
for resource in scraped_resources:
    resource.type = groq_service.classify_resource_type(url, title)
    resource.skills = groq_service.extract_skills(description)
    resource.difficulty = groq_service.assess_difficulty(content, user_skills)
```

**API Endpoint**:
- `POST /api/resources/search` - Search across all platforms
- `GET /api/resources/platforms/{platform}` - Filter by platform

---

### Phase 5: Progress Tracking & Adaptation

**Objective**: Monitor progress and adapt roadmap dynamically

```
User Progress → ProgressService.analyze_progress()
              ├─→ Calculate: completion rate, pace, struggles
              ├─→ Groq: Quick difficulty assessment
              ├─→ Gemini: Generate recommendations
              └─→ If struggling → Adapt roadmap
                  ├─ Add reinforcement milestones
                  ├─ Extend durations
                  ├─ Suggest targeted resources
                  └─ Update roadmap in DB
```

**Adaptive Triggers**:
1. User struggling with same skill for 3+ checkpoints
2. Moving too fast/slow (based on time spent vs. completion)
3. Low checkpoint submission rate
4. User requests help

**Checkpoint Submission Flow**:
```
User submits checkpoint → LLM analyzes submission
                        → Provides feedback
                        → Tracks progress
                        → Checks if adaptation needed
                        → If yes, adjust roadmap
```

**API Endpoints**:
- `POST /api/milestone/{id}/start` - Start milestone
- `POST /api/checkpoint/{id}/submit` - Submit checkpoint
- `GET /api/progress/{roadmap_id}` - Get progress stats
- `GET /api/progress/{roadmap_id}/analysis` - AI analysis
- `POST /api/roadmap/{id}/adapt` - Trigger roadmap adaptation

---

## 🤖 AI Service Distribution

### Gemini 2.5 Flash (Primary LLM) - Complex Tasks
**Free Tier**: 1500 requests/day

Used for:
- ✅ Onboarding conversations (natural language)
- ✅ Project generation (creative, structured output)
- ✅ Roadmap generation (strategic planning)
- ✅ Resource ranking (complex relevance assessment)
- ✅ Progress recommendations (holistic analysis)
- ✅ Checkpoint feedback (detailed analysis)

**Estimated Usage**: ~700 calls/day (47% of quota)

### Groq API (Llama 8B) - Fast, Simple Tasks
**Free Tier**: Very generous

Used for:
- ✅ Resource classification (type, difficulty)
- ✅ Skill extraction from text
- ✅ Content summarization
- ✅ Search query optimization
- ✅ Project requirement parsing
- ✅ Quick difficulty assessments

**Why Groq?**: 10x faster than Gemini for simple tasks, saves quota

### Local Embeddings (sentence-transformers)
**Cost**: $0 (runs locally, CPU-optimized)

Used for:
- ✅ Generate embeddings for all text (queries, resources, projects)
- ✅ Enable semantic search in Qdrant
- ✅ Find similar projects/resources
- ✅ RAG context retrieval

**Model**: all-MiniLM-L6-v2 (80MB, 384-dim, fast on CPU)

---

## 🔗 Context Connection: Projects ↔ Roadmaps ↔ Resources

### How Everything Connects

```
Project: "Build E-commerce Platform"
   ↓
Roadmap Generated:
   - Milestone 1: Setup (Django + React)
   - Milestone 2: Authentication
   - Milestone 3: Product Catalog
   - Milestone 4: Cart & Payments
   ↓
Resources Auto-Linked:
   - Milestone 1 → [Django tutorial (YouTube), React docs (Web), Starter template (GitHub)]
   - Milestone 2 → [JWT auth guide (Stack Overflow), Django REST tutorial (YouTube)]
   - Milestone 3 → [Database design (Article), PostgreSQL tips (Reddit)]
   - Milestone 4 → [Stripe integration (GitHub), Payment security (Stack Overflow)]
```

### RAG in Action

When user asks: "How do I implement authentication in Django?"

```
Question → Generate embedding (local)
        → Search Qdrant for similar content
        → Retrieve top 3 relevant resources
        → Pass to Gemini with context
        → Generate answer citing specific resources
```

**This creates a ONE-STOP experience**: No need to jump between platforms!

---

## 📊 Data Models

### Core Models

**User Profile** (MongoDB)
```python
{
    "_id": "user_123",
    "email": "user@example.com",
    "experience_level": "intermediate",
    "interests": ["web dev", "AI"],
    "skills": ["Python", "JavaScript"],
    "primary_goal": "portfolio",
    "time_commitment": "10 hours/week"
}
```

**Project** (MongoDB)
```python
{
    "_id": "proj_456",
    "user_id": "user_123",
    "title": "Task Manager App",
    "description": "...",
    "tech_stack": ["React", "FastAPI", "PostgreSQL"],
    "difficulty": "intermediate",
    "estimated_weeks": 4,
    "status": "in_progress",
    "roadmap_id": "roadmap_789"
}
```

**Roadmap** (MongoDB)
```python
{
    "_id": "roadmap_789",
    "project_id": "proj_456",
    "milestones": [...],
    "current_milestone_id": "milestone_2",
    "progress_percentage": 45.0,
    "is_adaptive": true,
    "adaptations": [
        {
            "type": "add_reinforcement",
            "skill": "React Hooks",
            "timestamp": "2024-01-15"
        }
    ]
}
```

**Resource** (Qdrant Vector DB)
```python
{
    "id": "res_abc",
    "vector": [0.123, 0.456, ...],  # 384-dim embedding
    "payload": {
        "title": "React Hooks Tutorial",
        "url": "https://youtube.com/...",
        "source": "youtube",
        "type": "video",
        "skills": ["React", "JavaScript"],
        "difficulty": "beginner",
        "description": "..."
    }
}
```

---

## 🚀 API Quick Reference

### Onboarding
- `POST /api/onboarding/chat` - Chat with onboarding AI
- `POST /api/onboarding/complete` - Finish onboarding

### Projects
- `GET /api/projects/recommended` - Get AI recommendations
- `POST /api/projects/generate` - Generate custom project
- `GET /api/projects/{id}/roadmap` - Get project roadmap

### Resources
- `POST /api/resources/search` - Multi-platform search
- `GET /api/resources/recommended` - Context-aware recommendations
- `GET /api/resources/platforms/{platform}` - Platform-specific

### Progress & Roadmap
- `POST /api/milestone/{id}/start` - Start milestone
- `POST /api/checkpoint/{id}/submit` - Submit checkpoint
- `GET /api/progress/{roadmap_id}/analysis` - AI analysis
- `POST /api/roadmap/{id}/adapt` - Adapt roadmap
- `GET /api/struggling/{skill}` - Get help resources

---

## 🎓 Example User Flow

1. **Day 1**: Complete onboarding → Get 5 project recommendations
2. **Day 2**: Select "Build Real-time Chat App" → Roadmap generated (5 milestones, 15 checkpoints)
3. **Week 1**: Complete Milestone 1 (Setup) → Submit 3 checkpoints → Get feedback
4. **Week 2**: Struggling with WebSockets → AI detects → Suggests YouTube tutorials + Stack Overflow answers
5. **Week 3**: Moving faster than expected → AI suggests advanced features
6. **Week 4**: Complete project → Get certificate + Next project recommendations

---

## 🔧 Setup Instructions

### 1. Environment Variables

Copy `.env.example` to `.env` and fill in:

**Required**:
- `GOOGLE_API_KEY` - Get from https://makersuite.google.com/app/apikey
- `GROQ_API_KEY` - Get from https://console.groq.com/keys

**Optional** (for better scraping):
- `QDRANT_URL` + `QDRANT_API_KEY` - For cloud vector DB
- `YOUTUBE_API_KEY` - For YouTube scraping
- `GITHUB_TOKEN` - For higher GitHub rate limits

### 2. Run Setup

```bash
./setup.sh
```

This installs:
- Python 3.12.2 (via pyenv)
- Node 20 (via nvm)
- All dependencies

### 3. Start Services

```bash
# Start MongoDB
mongod

# Start backend + frontend
./start.sh
```

### 4. Test the Flow

```
1. Open http://localhost:5173
2. Complete onboarding (3-4 questions)
3. View recommended projects
4. Select a project → See roadmap
5. Start milestone → Submit checkpoint
6. Search for resources
```

---

## 📈 Quota Management Strategy

**Goal**: Stay within free tiers

### Gemini API (1500/day limit)
- Onboarding: ~3-5 calls per user
- Project generation: ~1 call per batch (5 projects)
- Roadmap generation: ~1 call per project
- Checkpoint feedback: ~1 call per submission

**Optimization**:
- Use Groq for simple tasks (classification, extraction)
- Cache common responses in Redis
- Use local embeddings (0 API calls)
- Batch operations when possible

### Expected Daily Usage (100 active users)
- Onboarding: 50 users × 4 calls = 200
- Projects: 30 users × 1 call = 30
- Roadmaps: 20 users × 1 call = 20
- Checkpoints: 50 submissions × 1 call = 50
- Q&A: 100 questions × 1 call = 100
- **Total: ~400 calls/day (27% of quota)** ✅

---

## 🎯 Next Steps

**Immediate**:
- [ ] Add MongoDB CRUD operations
- [ ] Implement authentication (JWT)
- [ ] Add response caching (Redis)
- [ ] Test end-to-end flow

**Short-term**:
- [ ] Implement structured output parsing from LLM
- [ ] Add user analytics dashboard
- [ ] Create admin panel for monitoring
- [ ] Add export functionality (PDF roadmaps)

**Long-term**:
- [ ] Add collaborative features (share projects)
- [ ] Implement gamification (badges, leaderboards)
- [ ] Mobile app (React Native)
- [ ] Integration with more platforms (LinkedIn Learning, Udemy)

---

## 📚 Architecture Highlights

✅ **Hybrid AI**: Combines Gemini (powerful) + Groq (fast) + local embeddings (free)
✅ **Smart Orchestration**: LangChain manages complex workflows
✅ **Multi-source**: Aggregates from 5+ platforms in parallel
✅ **Adaptive Learning**: Roadmaps evolve based on user progress
✅ **Context-Aware**: RAG connects everything with semantic search
✅ **Quota-Optimized**: Stays within free tiers through smart routing
✅ **Scalable**: Modular services, easy to add more LLMs/platforms
