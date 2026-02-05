"""
Optimized Local Embeddings using sentence-transformers

This module provides efficient embedding functionality using local models
to avoid exhausting Gemini API free tier quota.

Key optimizations:
- Lazy model loading (only when needed)
- Batch processing for efficiency
- Model caching
- CPU-optimized (works without GPU)
"""

from typing import List, Optional, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch
from app.core.config import settings


class EmbeddingService:
    """Singleton service for handling embeddings efficiently"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize with lazy loading"""
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the embedding model (lazy loading)"""
        try:
            print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            
            # Use CPU or CUDA based on config
            device = settings.EMBEDDING_DEVICE
            if device == "cuda" and not torch.cuda.is_available():
                print("CUDA not available, falling back to CPU")
                device = "cpu"
            
            # Load lightweight model (all-MiniLM-L6-v2: 80MB, 384 dimensions)
            self._model = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                device=device
            )
            
            # Optimize for inference
            self._model.eval()
            
            print(f"✅ Model loaded on {device}")
            
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            self._model = None
    
    def encode(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        show_progress: bool = False,
    ) -> np.ndarray:
        """
        Encode texts to embeddings (batch processing for efficiency)
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for processing (default from config)
            show_progress: Show progress bar
            
        Returns:
            numpy array of embeddings
        """
        if self._model is None:
            raise RuntimeError("Embedding model not loaded")
        
        if not texts:
            return np.array([])
        
        batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE
        
        try:
            # Encode with batching for efficiency
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True,  # L2 normalization for better similarity
            )
            return embeddings
            
        except Exception as e:
            print(f"Error encoding texts: {e}")
            return np.array([])
    
    def encode_single(self, text: str) -> np.ndarray:
        """Encode a single text (convenience method)"""
        return self.encode([text])[0]
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        if self._model is None:
            return 384  # Default for all-MiniLM-L6-v2
        return self._model.get_sentence_embedding_dimension()


# Singleton instance
embedding_service = EmbeddingService()


async def get_embeddings(texts: List[str], batch_size: Optional[int] = None) -> List[np.ndarray]:
    """
    Get embeddings for texts (async wrapper)
    
    Args:
        texts: List of text strings to embed
        batch_size: Optional batch size override
        
    Returns:
        List of embedding vectors
    """
    try:
        embeddings = embedding_service.encode(texts, batch_size=batch_size)
        return [emb for emb in embeddings]
    except Exception as e:
        print(f"Error getting embeddings: {e}")
        return []


async def get_embedding(text: str) -> np.ndarray:
    """Get embedding for single text"""
    try:
        return embedding_service.encode_single(text)
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return np.array([])


async def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate cosine similarity between two texts
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-1)
    """
    try:
        embeddings = embedding_service.encode([text1, text2])
        if len(embeddings) != 2:
            return 0.0
        
        # Cosine similarity (already normalized, so just dot product)
        similarity = np.dot(embeddings[0], embeddings[1])
        
        return float(similarity)
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0


async def rank_by_relevance(
    query: str,
    documents: List[str],
    top_k: Optional[int] = None,
) -> List[tuple]:
    """
    Rank documents by relevance to query (optimized batch processing)
    
    Args:
        query: Search query
        documents: List of document texts
        top_k: Return top K results (None = all)
        
    Returns:
        List of (index, score) tuples sorted by relevance
    """
    try:
        # Encode query and documents in batch for efficiency
        all_texts = [query] + documents
        embeddings = embedding_service.encode(all_texts)
        
        if len(embeddings) < 2:
            return []
        
        query_emb = embeddings[0].reshape(1, -1)
        doc_embs = embeddings[1:]
        
        # Calculate similarities (fast with normalized embeddings)
        similarities = np.dot(doc_embs, query_emb.T).flatten()
        
        # Sort by relevance
        ranked_indices = np.argsort(similarities)[::-1]
        
        if top_k:
            ranked_indices = ranked_indices[:top_k]
        
        return [(int(idx), float(similarities[idx])) for idx in ranked_indices]
        
    except Exception as e:
        print(f"Error ranking documents: {e}")
        return []


async def find_similar_documents(
    query: str,
    documents: List[Dict],
    top_k: int = 5,
    threshold: float = 0.5,
) -> List[Dict]:
    """
    Find most similar documents to query
    
    Args:
        query: Search query
        documents: List of document dicts with 'content' field
        top_k: Number of results to return
        threshold: Minimum similarity threshold
        
    Returns:
        List of similar documents with scores
    """
    try:
        doc_texts = [doc.get("content", "") for doc in documents]
        ranked = await rank_by_relevance(query, doc_texts, top_k=top_k * 2)
        
        results = []
        for idx, score in ranked:
            if score >= threshold and len(results) < top_k:
                doc = documents[idx].copy()
                doc["relevance_score"] = float(score)
                results.append(doc)
        
        return results
        
    except Exception as e:
        print(f"Error finding similar documents: {e}")
        return []


def get_embedding_dimension() -> int:
    """Get the dimension of embeddings"""
    return embedding_service.get_dimension()
