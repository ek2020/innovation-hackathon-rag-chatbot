from typing import List, Dict, Any, Optional, Tuple
import os

from app.core.config import settings
from app.services.document_processor import process_document, match_resources_to_project
from app.services.vector_store import vector_store
from app.services.azure_openai import azure_openai_service
from app.services.conversation import conversation_service

class RAGService:
    """Service for RAG functionality."""
    
    def process_and_store_document(self, file_path: str) -> bool:
        """
        Process a document and store it in the vector database.
        
        Args:
            file_path: Path to the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Process the document
            chunks, metadatas = process_document(file_path)
            
            if not chunks:
                return False
            
            # Add text to each metadata for easier retrieval
            for i, metadata in enumerate(metadatas):
                metadata["text"] = chunks[i]
            
            # Store in vector database
            vector_store.add_documents(chunks, metadatas)
            
            return True
        except Exception as e:
            print(f"Error processing and storing document: {str(e)}")
            return False
    
    def process_directory(self, directory_path: str) -> Tuple[int, int]:
        """
        Process all documents in a directory.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            Tuple of (number of successful documents, total documents)
        """
        if not os.path.isdir(directory_path):
            return 0, 0
        
        successful = 0
        total = 0
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if not os.path.isfile(file_path):
                continue
            
            _, ext = os.path.splitext(filename)
            if ext.lower() not in ['.txt', '.pdf', '.docx']:
                continue
            
            total += 1
            if self.process_and_store_document(file_path):
                successful += 1
        
        return successful, total
    
    def query(
        self, 
        query: str, 
        session_id: str,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Perform a RAG query.
        
        Args:
            query: The query text
            session_id: The conversation session ID
            top_k: Number of results to return
            
        Returns:
            Query result
        """
        try:
            # Get conversation history
            conversation_history = conversation_service.get_conversation_history(session_id)
            
            # Contextualize the query if we have conversation history
            if conversation_history:
                contextualized_query = azure_openai_service.contextualize_query(
                    query, conversation_history
                )
            else:
                contextualized_query = query
            
            # Search for relevant documents
            texts, metadatas, scores = vector_store.search(contextualized_query, top_k)
            
            # Format context for the LLM
            context = "\n\n".join([
                f"Document: {metadata.get('source', 'Unknown')}\n{text}"
                for text, metadata in zip(texts, metadatas)
            ])
            
            # Generate response
            response = azure_openai_service.generate_rag_response(
                query=query,
                context=context,
                conversation_history=conversation_history
            )
            
            # Add to conversation history
            conversation_service.add_message(session_id, "user", query)
            conversation_service.add_message(session_id, "assistant", response)
            
            # Format sources
            sources = [
                {
                    "source": metadata.get("source", "Unknown"),
                    "chunk_index": metadata.get("chunk_index", 0),
                    "score": score
                }
                for metadata, score in zip(metadatas, scores)
            ]
            
            return {
                "query": query,
                "contextualized_query": contextualized_query,
                "response": response,
                "sources": sources
            }
            
        except Exception as e:
            print(f"Error performing RAG query: {str(e)}")
            return {
                "query": query,
                "contextualized_query": query,
                "response": f"Error: {str(e)}",
                "sources": []
            }
    
    def match_profiles_to_sow(
        self, 
        profile_file_paths: List[str], 
        sow_file_path: str
    ) -> List[Dict[str, Any]]:
        """
        Match profiles to a Statement of Work.
        
        Args:
            profile_file_paths: List of paths to profile documents
            sow_file_path: Path to the SOW document
            
        Returns:
            List of matches with scores
        """
        try:
            from app.services.document_processor import read_document
            
            # Read SOW document
            sow_text = read_document(sow_file_path)
            
            # Read profile documents
            profiles = []
            for file_path in profile_file_paths:
                try:
                    text = read_document(file_path)
                    name = os.path.basename(file_path)
                    profiles.append({
                        "name": name,
                        "text": text,
                        "file_path": file_path
                    })
                except Exception as e:
                    print(f"Error reading profile {file_path}: {str(e)}")
            
            # Match profiles to SOW
            matches = match_resources_to_project(profiles, sow_text)
            
            return matches
            
        except Exception as e:
            print(f"Error matching profiles to SOW: {str(e)}")
            return []

# Create a singleton instance
rag_service = RAGService()
