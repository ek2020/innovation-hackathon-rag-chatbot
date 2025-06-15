from typing import List, Dict, Any, Optional, Tuple
import uuid
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import settings
from app.services.azure_openai import azure_openai_service

class VectorStore:
    """Vector database service for storing and retrieving document embeddings."""
    
    def __init__(self):
        """Initialize the vector database client."""
        if settings.VECTOR_DB_TYPE == "qdrant":
            self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
            self._ensure_collection_exists()
        else:
            raise ValueError(f"Unsupported vector database type: {settings.VECTOR_DB_TYPE}")
    
    def _ensure_collection_exists(self):
        """Ensure that the collection exists in Qdrant."""
        try:
            # Check if collection exists
            self.client.get_collection(settings.QDRANT_COLLECTION_NAME)
            print(f"Collection {settings.QDRANT_COLLECTION_NAME} already exists")
        except (UnexpectedResponse, Exception) as e:
            print(f"Collection {settings.QDRANT_COLLECTION_NAME} does not exist: {str(e)}")
            # Create collection if it doesn't exist
            print(f"Creating collection {settings.QDRANT_COLLECTION_NAME} with vector size {settings.QDRANT_VECTOR_SIZE}")
            self.client.create_collection(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=settings.QDRANT_VECTOR_SIZE,
                    distance=models.Distance.COSINE
                )
            )
            print(f"Collection {settings.QDRANT_COLLECTION_NAME} created successfully")
    
    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of document texts
            metadatas: List of metadata dictionaries
            
        Returns:
            List of document IDs
        """
        if not texts or len(texts) != len(metadatas):
            return []
        
        # Generate embeddings
        embeddings = azure_openai_service.generate_embeddings(texts)
        
        # Generate IDs
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        
        # Add points to Qdrant
        self.client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=models.Batch(
                ids=ids,
                vectors=embeddings,
                payloads=metadatas
            )
        )
        
        return ids
    
    def search(
        self, 
        query: str, 
        top_k: int = 3
    ) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
        """
        Search for similar documents.
        
        Args:
            query: The query text
            top_k: Number of results to return
            
        Returns:
            Tuple of (texts, metadatas, scores)
        """
        # Generate query embedding
        query_embedding = azure_openai_service.generate_embeddings([query])[0]
        
        # Search in Qdrant
        search_results = self.client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True
        )
        
        # Extract results
        texts = []
        metadatas = []
        scores = []
        
        for result in search_results:
            # Get the document ID
            doc_id = result.id
            
            # Get the document payload (metadata)
            metadata = result.payload
            
            # Get the similarity score
            score = result.score
            
            # Get the document text from the payload
            text = metadata.get("text", "")
            if not text:
                # If text is not in payload, we need to fetch it from the source
                # This is a simplified approach - in a real system, you might store the text in the payload
                # or have a separate database for document storage
                source = metadata.get("source", "")
                chunk_index = metadata.get("chunk_index", 0)
                text = f"Document: {source}, Chunk: {chunk_index}"
            
            texts.append(text)
            metadatas.append(metadata)
            scores.append(score)
        
        return texts, metadatas, scores
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            doc_id: The document ID
            
        Returns:
            Document data or None if not found
        """
        try:
            points = self.client.retrieve(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                ids=[doc_id],
                with_payload=True,
                with_vectors=True
            )
            
            if points and len(points) > 0:
                point = points[0]
                return {
                    "id": point.id,
                    "metadata": point.payload,
                    "vector": point.vector
                }
            
            return None
            
        except Exception as e:
            print(f"Error retrieving document: {str(e)}")
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            doc_id: The document ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                points_selector=models.PointIdsList(
                    points=[doc_id]
                )
            )
            return True
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete the collection
            self.client.delete_collection(settings.QDRANT_COLLECTION_NAME)
            
            # Recreate the collection
            self._ensure_collection_exists()
            
            return True
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")
            return False

# Create a singleton instance
vector_store = VectorStore()
