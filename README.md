# AI-Powered Project-Based Learning Platform

A comprehensive learning platform that provides personalized project recommendations and curated resources based on user's experience, goals, and interests.
# Team - Devanshu pal baghel , Devansh sharma, Dev sharma
## 🚀 Features

### 1. AI-Powered Onboarding
- Interactive chatbot for personalized onboarding
- 3-4 intelligent questions based on user responses
- Collects: current level, goals, interests, and past experiences
- Custom question flow based on previous answers

### 2. Projects Dashboard
- **Project Recommendations**: AI-curated projects based on onboarding data
- **Project Roadmaps**: Step-by-step guides with resources
- **Checkpoints System**: Upload screenshots and track progress
- **AI Progress Analysis**: LLM analyzes user submissions and provides feedback
- **Project Generation**: Generate custom project ideas

### 3. Resources Hub
- Multi-platform resource aggregation (GitHub, Reddit, YouTube, Stack Overflow)
- Intelligent web scraping for relevant materials
- Contextual resource recommendations
- Search and filter capabilities

### 4. Multi-Domain Support
- Not limited to specific domains
- Adapts to user's chosen field of interest
- Dynamic content curation

## 🛠️ Tech Stack

### Frontend
- **React.js**: UI framework
- **Tailwind CSS**: Utility-first styling (no PostCSS)
- **Responsive Design**: Mobile-first approach

### Backend
- **FastAPI**: High-performance Python web framework
- **MongoDB**: NoSQL database for flexible data storage
- **Google Gemini 2.5 Flash**: LLM for AI-powered features (free tier)
- **LangChain**: RAG and orchestration framework
- **sentence-transformers**: Local embeddings (all-MiniLM-L6-v2, no GPU required)
- **Qdrant**: Lightweight vector database for similarity search

### AI/ML Architecture
- **Embeddings**: Local sentence-transformers (no API calls, saves quota)
- **Vector DB**: Qdrant for fast similarity search
- **LLM**: Google Gemini 2.5 Flash for text generation
- **RAG**: Retrieval Augmented Generation using local embeddings + Qdrant
- **Optimization**: Hybrid approach to minimize API usage

### Development Tools
- **pyenv**: Python version management (3.12.2)
- **nvm**: Node.js version management (v20)

## 📁 Project Structure

```
project-based-learning/
├── frontend/                 # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/      # Global reusable components
│   │   ├── pages/           # Page components with nested structure
│   │   ├── styles/          # Global styles
│   │   ├── hooks/           # Custom React hooks
│   │   ├── utils/           # Utility functions
│   │   ├── services/        # API services
│   │   └── App.jsx
│   └── package.json
│
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configurations
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── main.py
│   └── requirements.txt
│
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- **pyenv** (for Python version management)
- **nvm** (for Node.js version management)
- **MongoDB**
- **Google Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Quick Setup

Run the automated setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Set Python 3.12.2 as local version (via pyenv)
- Set Node.js 20 as active version (via nvm)
- Install all frontend and backend dependencies
- Create environment files

### Manual Setup

#### Frontend

```bash
cd frontend
nvm use 20  # or nvm install 20 && nvm use 20
npm install
npm run dev
```

#### Backend

```bash
cd backend
pyenv local 3.12.2  # Ensure Python 3.12.2 is installed
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

### Environment Variables

Create `.env` files in both frontend and backend directories:

**Frontend `.env`:**
```
VITE_API_BASE_URL=http://localhost:8000/api
```

**Backend `.env`:**
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ai_learn_hub
SECRET_KEY=your-secret-key-here

# Google Gemini API (Free Tier)
GOOGLE_API_KEY=your-google-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash-exp

# Local Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu

# Qdrant Vector DB
QDRANT_USE_MEMORY=true
```

**Get your Google Gemini API key:** https://makersuite.google.com/app/apikey

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete AI architecture and data flow
- **[OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)** - Quota optimization guide
- **[SETUP.md](SETUP.md)** - Detailed setup instructions

## 📝 Development Guidelines

1. **Component Structure**: Each page folder contains its own `components/` folder and `index.jsx`
2. **Global Components**: Reusable components in `src/components/`
3. **Tailwind Usage**: Use Tailwind utility classes, maintain consistency
4. **Responsive Design**: Mobile-first approach from the start
5. **Code Organization**: Keep logic in `index.jsx`, UI in components

## 🎯 Roadmap

- [ ] Phase 1: Core infrastructure setup
- [ ] Phase 2: Onboarding chatbot implementation
- [ ] Phase 3: Project recommendation engine
- [ ] Phase 4: Resource scraping and aggregation
- [ ] Phase 5: Checkpoint and progress tracking system
- [ ] Phase 6: AI progress analysis
- [ ] Phase 7: Testing and optimization

## 👥 Team

Mini-Project Class Subject

## 📄 License

MIT License
