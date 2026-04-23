from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Project Info
    PROJECT_NAME: str = "AI-Learn Hub API"
    VERSION: str = "1.0.0"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "ai_learn_hub"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Google Gemini API (Free Tier - 2.5 Flash) - Main LLM
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"  # Free tier model
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2048
    GEMINI_ENABLE_ONBOARDING_CHAT: bool = False
    GEMINI_ENABLE_PROJECT_GENERATION: bool = False
    
    # Groq API (Lightweight Llama models) - Secondary LLM for simple tasks
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"  # Fast, efficient for simple tasks
    GROQ_TEMPERATURE: float = 0.5
    GROQ_MAX_TOKENS: int = 1024
    
    # Embeddings (Local - sentence-transformers)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # 80MB, fast, good quality
    EMBEDDING_DEVICE: str = "cpu"  # or "cuda" if GPU available
    EMBEDDING_BATCH_SIZE: int = 32
    
    # Vector Database - Qdrant
    QDRANT_URL: str = ""  # Cloud URL from env (e.g., https://xxx.cloud.qdrant.io:6333)
    QDRANT_API_KEY: str = ""  # API key for Qdrant cloud
    QDRANT_HOST: str = "localhost"  # Fallback for local development
    QDRANT_PORT: int = 6333
    QDRANT_LOCAL_PATH: str = ".qdrant_data"  # Local persisted embedded storage
    QDRANT_COLLECTION: str = "learning_resources"
    QDRANT_USE_MEMORY: bool = True  # In-memory mode for development
    QDRANT_USE_CLOUD: bool = False  # Set to True to use cloud instance
    
    # LangChain Settings
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: str = ""
    
    # Redis (for caching)
    REDIS_URL: str = "redis://localhost:6379"
    
    # External APIs for scraping
    GITHUB_TOKEN: str = ""  # Optional, for higher rate limits
    YOUTUBE_API_KEY: str = ""  # For YouTube Data API v3
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    GOOGLE_SEARCH_API_KEY: str = ""  # For Custom Search API
    GOOGLE_SEARCH_ENGINE_ID: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
