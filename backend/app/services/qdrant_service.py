"""
Qdrant Vector Database Service

Handles vector storage and similarity search using Qdrant.
More efficient than ChromaDB with better performance.
"""

from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from app.core.config import settings
from app.utils.embeddings import embedding_service, get_embedding
import uuid


class QdrantService:
    """Service for interacting with Qdrant vector database"""
    
    def __init__(self):
        """Initialize Qdrant client"""
        self.client = None
        self.collection_name = settings.QDRANT_COLLECTION
        self.embedding_dim = embedding_service.get_dimension()
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Qdrant client (memory, local server, or cloud mode)"""
        try:
            if settings.QDRANT_USE_CLOUD and settings.QDRANT_URL and settings.QDRANT_API_KEY:
                # Cloud mode (production)
                print(f"Connecting to Qdrant Cloud: {settings.QDRANT_URL}")
                self.client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY,
                )
            elif settings.QDRANT_USE_MEMORY:
                # In-memory mode (for development)
                print("Initializing Qdrant in memory mode...")
                self.client = QdrantClient(":memory:")
            else:
                # Local server mode
                print(f"Connecting to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
                self.client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                )
            
            # Create collection if it doesn't exist
            self._ensure_collection()
            
            print("✅ Qdrant initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing Qdrant: {e}")
            self.client = None
    
    def _ensure_collection(self):
        """Ensure collection exists with correct configuration"""
        try:
            collections = self.client.get_collections().collections
            collection_exists = any(
                col.name == self.collection_name for col in collections
            )
            
            if not collection_exists:
                print(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE,
                    ),
                )
                print(f"✅ Collection '{self.collection_name}' created")
            else:
                print(f"Collection '{self.collection_name}' already exists")
                
        except Exception as e:
            print(f"Error ensuring collection: {e}")
    
    async def add_documents(
        self,
        documents: List[Dict],
        batch_size: int = 100,
    ) -> bool:
        """
        Add documents to Qdrant with embeddings
        
        Args:
            documents: List of dicts with 'content' and optional 'metadata'
            batch_size: Batch size for processing
            
        Returns:
            Success status
        """
        if not self.client:
            print("Qdrant client not initialized")
            return False
        
        try:
            # Extract texts
            texts = [doc.get("content", "") for doc in documents]
            
            # Generate embeddings in batch (efficient)
            print(f"Generating embeddings for {len(texts)} documents...")
            embeddings = embedding_service.encode(texts, batch_size=batch_size)
            
            # Create points for Qdrant
            points = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                point_id = doc.get("id", str(uuid.uuid4()))
                
                # Prepare payload (metadata)
                payload = {
                    "content": doc.get("content", ""),
                    **doc.get("metadata", {}),
                }
                
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=embedding.tolist(),
                        payload=payload,
                    )
                )
            
            # Upload to Qdrant in batches
            print(f"Uploading {len(points)} points to Qdrant...")
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                )
            
            print(f"✅ Successfully added {len(points)} documents")
            return True
            
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.5,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Search query text
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            filters: Optional metadata filters
            
        Returns:
            List of matching documents with scores
        """
        if not self.client:
            print("Qdrant client not initialized")
            return []
        
        try:
            # Generate query embedding
            query_embedding = await get_embedding(query)
            
            if query_embedding.size == 0:
                return []
            
            # Build filter if provided
            search_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
                if conditions:
                    search_filter = Filter(must=conditions)
            
            # Search in Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=search_filter,
            )
            
            # Format results
            documents = []
            for result in results:
                doc = {
                    "id": result.id,
                    "score": result.score,
                    "content": result.payload.get("content", ""),
                    "metadata": {
                        k: v for k, v in result.payload.items()
                        if k != "content"
                    },
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    async def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents by IDs"""
        if not self.client:
            return False
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=ids,
            )
            print(f"✅ Deleted {len(ids)} documents")
            return True
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return False
    
    def get_collection_info(self) -> Dict:
        """Get collection statistics"""
        if not self.client:
            return {}
        
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {}
    
    def clear_collection(self) -> bool:
        """Clear all documents from collection"""
        if not self.client:
            return False
        
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection()
            print(f"✅ Collection '{self.collection_name}' cleared")
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False


# Singleton instance
qdrant_service = QdrantService()
