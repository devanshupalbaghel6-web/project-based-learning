# AI Architecture - Optimized for Gemini 2.5 Flash Free Tier

## Overview

This project uses **local sentence-transformers** for embeddings and **Google Gemini 2.5 Flash** for text generation to minimize API quota usage on the free tier.

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      USER REQUEST                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. EMBEDDINGS (Local - No API Calls)                │   │
│  │     • sentence-transformers (all-MiniLM-L6-v2)       │   │
│  │     • CPU-optimized, 80MB model                      │   │
│  │     • Lazy loading + batching                        │   │
│  │     • 384-dim vectors                                │   │
│  └──────────────────────────────────────────────────────┘   │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  2. VECTOR STORAGE (Qdrant)                          │   │
│  │     • In-memory mode (dev) / Server mode (prod)      │   │
│  │     • Fast similarity search                         │   │
│  │     • Metadata filtering                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  3. RAG (Retrieval)                                  │   │
│  │     • Query → local embedding                        │   │
│  │     • Search Qdrant for top-k similar docs           │   │
│  │     • Build context from results                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  4. LLM GENERATION (Gemini 2.5 Flash - API)          │   │
│  │     • Context + Query → Gemini API                   │   │
│  │     • Minimal prompts to save tokens                 │   │
│  │     • Response caching where possible                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    RESPONSE TO USER                          │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. **Embeddings Service** (`app/utils/embeddings.py`)

**What:** Converts text to 384-dimensional vectors
**How:** sentence-transformers (all-MiniLM-L6-v2 model)
**Where:** Runs locally on CPU
**Why:** Avoid Gemini embedding API calls to save quota

**Key Features:**
- Lazy model loading (loaded only when first used)
- Batch processing (process multiple texts at once)
- L2 normalization for better similarity
- CPU-optimized (no CUDA required)

**Usage:**
```python
from app.utils.embeddings import embedding_service

# Single text
embedding = embedding_service.encode_single("Hello world")

# Multiple texts (batched for efficiency)
embeddings = embedding_service.encode([
    "Text 1", "Text 2", "Text 3"
], batch_size=32)
```

### 2. **Qdrant Service** (`app/services/qdrant_service.py`)

**What:** Vector database for similarity search
**How:** Qdrant client (in-memory or server mode)
**Where:** Local (development) or Qdrant server (production)
**Why:** More efficient than ChromaDB, better performance

**Key Features:**
- In-memory mode for development (no setup needed)
- Server mode for production
- Metadata filtering
- Batch upserts

**Usage:**
```python
from app.services.qdrant_service import qdrant_service

# Add documents (embeddings generated automatically)
await qdrant_service.add_documents([
    {"content": "How to build a RAG system", "metadata": {"type": "tutorial"}},
    {"content": "Python FastAPI guide", "metadata": {"type": "guide"}},
])

# Search (query embedding generated automatically)
results = await qdrant_service.search(
    query="RAG implementation",
    top_k=5,
    score_threshold=0.7,
    filters={"type": "tutorial"}
)
```

### 3. **LLM Service** (`app/services/llm_service.py`)

**What:** Text generation using Gemini
**How:** LangChain + Google Gemini 2.5 Flash API
**Where:** Google Cloud (API calls)
**Why:** Free tier with good performance

**Optimizations:**
- Minimal prompts (fewer tokens = less quota usage)
- RAG for context (instead of long prompts)
- Response caching
- Conversation memory management

**Usage:**
```python
from app.services.llm_service import llm_service

# Simple generation
response = await llm_service.generate_onboarding_response(
    user_message="I want to learn AI",
    conversation_history=[]
)

# RAG-based response
response = await llm_service.generate_response_with_rag(
    query="How do I build a chatbot?",
    top_k=3
)
```

## API Quota Management

### Gemini 2.5 Flash Free Tier Limits:
- **15 requests per minute**
- **1,500 requests per day**
- **1 million tokens per day**

### How We Minimize Usage:

1. **Use Local Embeddings**
   - ❌ Don't use Gemini embedding API
   - ✅ Use sentence-transformers locally
   - **Savings:** ~500-1000 API calls per day

2. **RAG with Local Vectors**
   - ❌ Don't send long context in prompts
   - ✅ Retrieve relevant chunks, send only top 3
   - **Savings:** 50-70% fewer tokens per request

3. **Concise Prompts**
   - Keep prompts under 100 tokens
   - Use structured formats
   - Avoid verbose instructions

4. **Caching**
   - Cache common responses
   - Reuse conversation memory
   - Store project templates in Qdrant

## Data Flow Examples

### Example 1: Resource Search

```
User: "Find Python tutorials"
  ↓
1. Generate embedding locally (all-MiniLM-L6-v2)
   └─> [0.23, -0.45, 0.12, ...] (384 dims)
  ↓
2. Search Qdrant
   └─> Top 5 similar resources from vector DB
  ↓
3. Return results (NO LLM CALL NEEDED)
```

**API calls:** 0 ✅

### Example 2: Project Generation

```
User: "Generate a chatbot project"
  ↓
1. Generate query embedding locally
  ↓
2. Search Qdrant for similar project templates
   └─> Found 3 relevant templates
  ↓
3. Build minimal prompt:
   "User wants chatbot. Level: beginner.
    Similar: [template1, template2, template3]
    Generate project plan."
  ↓
4. Call Gemini 2.5 Flash (1 API call)
  ↓
5. Return generated project
```

**API calls:** 1 (for generation only) ✅

### Example 3: Onboarding Chat

```
User: "I want to learn web development"
  ↓
1. Build conversational prompt (minimal)
   └─> Include only last 2 messages (not full history)
  ↓
2. Call Gemini 2.5 Flash (1 API call)
  ↓
3. Get next question
```

**API calls:** 1 per message ✅

## Performance Benchmarks

### Embedding Generation (Local)
- Single text: ~10-20ms (CPU)
- Batch of 32: ~200-300ms (CPU)
- Batch of 100: ~500-700ms (CPU)

### Vector Search (Qdrant)
- Search with filters: ~5-10ms
- Top-10 retrieval: ~3-5ms

### LLM Generation (Gemini API)
- Simple prompt: ~500-1000ms
- Complex prompt: ~1000-2000ms
- Network latency: ~100-200ms

## Configuration

All settings in `backend/app/core/config.py`:

```python
# LLM Settings
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Free tier
GEMINI_TEMPERATURE = 0.7
GEMINI_MAX_TOKENS = 2048

# Embeddings (Local)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 80MB, fast
EMBEDDING_DEVICE = "cpu"  # or "cuda"
EMBEDDING_BATCH_SIZE = 32

# Qdrant
QDRANT_USE_MEMORY = True  # Dev mode
QDRANT_COLLECTION = "learning_resources"
```

## Deployment Considerations

### Development
- Use in-memory Qdrant
- CPU embeddings (fine for low volume)
- Gemini free tier

### Production
- Deploy Qdrant server (Docker)
- Consider GPU for embeddings if high volume
- Monitor Gemini quota usage
- Implement rate limiting

## Estimated Costs (Free Tier)

Assuming 100 users/day, 10 interactions each:

| Operation | Count/Day | API Calls | Quota Used |
|-----------|-----------|-----------|------------|
| Resource searches | 500 | 0 | 0% (local) |
| Onboarding chats | 400 | 400 | 27% |
| Project generation | 100 | 100 | 7% |
| Checkpoint analysis | 200 | 200 | 13% |
| **Total** | | **700** | **~47%** |

✅ Well within free tier limits!

## Alternative: If Quota Runs Out

If you hit quota limits:

1. **Use Smaller Model**
   - Switch to gemini-1.5-flash
   - Lower max_tokens to 1024

2. **Implement Caching**
   - Cache common responses
   - Use Redis for session memory

3. **Batch Operations**
   - Queue requests
   - Process in batches during off-peak

4. **Local Alternatives**
   - Use Ollama for local LLM (llama3, mistral)
   - Fully offline mode
