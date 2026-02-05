# 🚀 Quick Start Guide

## Prerequisites

- Python 3.12+ (managed by pyenv)
- Node.js 20+ (managed by nvm)
- MongoDB
- Git

## Installation Steps

### 1. Clone & Setup

```bash
cd "/home/devanshu/Downloads/project based learning"

# Run automated setup
chmod +x setup.sh start.sh
./setup.sh
```

This script will:
- ✅ Check for pyenv and nvm
- ✅ Install Python 3.12.2
- ✅ Install Node.js 20
- ✅ Create Python virtual environment
- ✅ Install all dependencies (backend + frontend)

### 2. Configure Environment Variables

```bash
cd backend
cp .env.example .env
nano .env  # or use your favorite editor
```

**Minimum required configuration**:

```env
# Get from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_key_here

# Get from: https://console.groq.com/keys
GROQ_API_KEY=your_key_here

# Optional: Qdrant Cloud (for production)
# Get from: https://cloud.qdrant.io/
QDRANT_URL=
QDRANT_API_KEY=
QDRANT_USE_CLOUD=false  # Keep false for local dev
```

**Optional APIs** (for better scraping):

```env
# YouTube Data API v3
# Get from: https://console.cloud.google.com/apis/credentials
YOUTUBE_API_KEY=

# GitHub Personal Access Token
# Get from: https://github.com/settings/tokens
GITHUB_TOKEN=

# Google Custom Search
# Get from: https://programmablesearchengine.google.com/
GOOGLE_SEARCH_API_KEY=
GOOGLE_SEARCH_ENGINE_ID=
```

### 3. Start MongoDB

```bash
# Option 1: Using mongod directly
mongod

# Option 2: Using Homebrew (macOS)
brew services start mongodb-community

# Option 3: Using systemd (Linux)
sudo systemctl start mongod
```

Verify MongoDB is running:
```bash
mongosh
# Should connect successfully
```

### 4. Start the Application

```bash
# From project root
./start.sh
```

This will:
- ✅ Start backend on http://localhost:8000
- ✅ Start frontend on http://localhost:5173

### 5. Verify Installation

Open your browser:
- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

---

## Testing the Flow

### 1. Test Onboarding

**Via Frontend**:
1. Navigate to http://localhost:5173
2. You'll see the onboarding chat interface
3. Answer 3-4 questions about your learning goals

**Via API** (using curl or Postman):

```bash
curl -X POST http://localhost:8000/api/onboarding/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to learn web development",
    "user_id": "test_user_123",
    "context": {}
  }'
```

### 2. Test Project Generation

```bash
curl -X POST http://localhost:8000/api/projects/generate?prompt=todo%20app&user_level=intermediate
```

### 3. Test Resource Search

```bash
curl -X POST http://localhost:8000/api/resources/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "React hooks tutorial",
    "platforms": ["youtube", "github"],
    "difficulty": "beginner"
  }'
```

### 4. Test Platform-Specific Search

```bash
# GitHub repositories
curl http://localhost:8000/api/resources/platforms/github

# YouTube videos
curl http://localhost:8000/api/resources/platforms/youtube

# Stack Overflow
curl http://localhost:8000/api/resources/platforms/stackoverflow
```

---

## API Endpoints Overview

### Onboarding
- `POST /api/onboarding/chat` - Chat with AI during onboarding
- `POST /api/onboarding/complete` - Complete onboarding

### Projects
- `GET /api/projects/recommended` - Get personalized project recommendations
- `POST /api/projects/generate` - Generate custom project
- `GET /api/projects/{id}/roadmap` - Get learning roadmap

### Resources
- `POST /api/resources/search` - Multi-platform resource search
- `GET /api/resources/recommended` - Context-aware recommendations
- `GET /api/resources/platforms/{platform}` - Platform-specific resources

### Progress & Roadmap
- `POST /api/milestone/{id}/start` - Start working on milestone
- `POST /api/checkpoint/{id}/submit` - Submit checkpoint for review
- `GET /api/progress/{roadmap_id}` - Get progress statistics
- `GET /api/progress/{roadmap_id}/analysis` - Get AI progress analysis
- `POST /api/roadmap/{id}/adapt` - Adapt roadmap based on progress
- `GET /api/struggling/{skill}` - Get help resources for struggling skill
- `GET /api/dashboard` - User's learning dashboard

---

## Troubleshooting

### Backend won't start

**Issue**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ..
./start.sh
```

### MongoDB connection error

**Issue**: `pymongo.errors.ServerSelectionTimeoutError`

**Solution**:
```bash
# Check if MongoDB is running
pgrep mongod

# If not, start it
mongod

# Or use system service
sudo systemctl start mongod
```

### Qdrant errors

**Issue**: `QdrantException: Connection error`

**Solution**: For development, use in-memory mode (default):
```env
QDRANT_USE_MEMORY=true
QDRANT_USE_CLOUD=false
```

### LLM API errors

**Issue**: `google.api_core.exceptions.PermissionDenied`

**Solution**:
1. Verify your API key is correct in `.env`
2. Check quota at https://makersuite.google.com/app/apikey
3. Ensure you've enabled the Gemini API in Google Cloud Console

**Issue**: `groq.APIError: Invalid API key`

**Solution**:
1. Get a new API key from https://console.groq.com/keys
2. Update `GROQ_API_KEY` in `.env`

### Scraping returns empty results

**Issue**: No YouTube/GitHub results

**Solution**: 
1. Check if API keys are configured (optional but recommended)
2. For development, at least one platform should work without keys (Reddit, Stack Overflow)
3. Enable API keys for better results:
   - YouTube: https://console.cloud.google.com/apis/credentials
   - GitHub: https://github.com/settings/tokens

---

## Development Tips

### Running Backend Only

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Frontend Only

```bash
cd frontend
npm run dev
```

### Viewing Logs

```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend console
# Open browser DevTools → Console
```

### Testing Individual Services

```python
# Test LLM service
cd backend
source venv/bin/activate
python -c "
from app.services.llm_service import llm_service
import asyncio

async def test():
    result = await llm_service.generate_onboarding_response(
        user_message='I want to learn Python',
        conversation_history=[]
    )
    print(result)

asyncio.run(test())
"
```

```python
# Test scraper
python -c "
from app.services.scraper_service import scraper_service
import asyncio

async def test():
    results = await scraper_service.search_github('python tutorial', 5)
    for repo in results:
        print(f'{repo[\"title\"]}: {repo[\"stars\"]} stars')

asyncio.run(test())
"
```

### Database Inspection

```bash
# Connect to MongoDB
mongosh

# Use database
use ai_learn_hub

# Show collections
show collections

# Query users
db.users.find().pretty()

# Query projects
db.projects.find().pretty()
```

---

## Next Steps

After setup is complete:

1. **Complete onboarding** to get personalized project recommendations
2. **Select a project** to generate a learning roadmap
3. **Start a milestone** and submit checkpoints
4. **Search for resources** when you need help
5. **Track your progress** and watch the roadmap adapt

---

## Getting Help

- 📖 Full architecture: See `COMPLETE_ARCHITECTURE.md`
- 🔧 API optimization: See `OPTIMIZATION_SUMMARY.md`
- 📋 Project structure: See `ARCHITECTURE.md`
- 🐛 Issues: Check troubleshooting section above

---

## Architecture Highlights

This platform uses:
- **Dual LLM Strategy**: Gemini (complex) + Groq (fast)
- **Local Embeddings**: sentence-transformers (no API costs)
- **Multi-Platform Scraping**: GitHub, YouTube, Reddit, Stack Overflow, Google
- **Adaptive Roadmaps**: Adjust based on your progress
- **RAG Pipeline**: Context-aware answers using Qdrant

**Free Tier Optimized**: ~400 API calls/day (well within limits!)
