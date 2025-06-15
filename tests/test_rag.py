#!/usr/bin/env python3
"""
Test script for RAG functionality.
"""

import os
import sys
import unittest
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from app.services.document_processor import process_document, read_document
from app.services.vector_store import vector_store
from app.services.azure_openai import azure_openai_service
from app.services.conversation import conversation_service
from app.services.rag_service import rag_service

class TestRAG(unittest.TestCase):
    """Test cases for RAG functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Sample documents
        cls.sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_documents")
        cls.company_profile = os.path.join(cls.sample_dir, "company_profile.txt")
        cls.developer_profile = os.path.join(cls.sample_dir, "developer_profile.txt")
        cls.project_sow = os.path.join(cls.sample_dir, "project_sow.txt")
        
        # Create a test session
        cls.session_id = conversation_service.create_session()
    
    def test_document_processing(self):
        """Test document processing functionality."""
        # Test reading a document
        content = read_document(self.company_profile)
        self.assertIsNotNone(content)
        self.assertGreater(len(content), 0)
        
        # Test processing a document
        chunks, metadatas = process_document(self.company_profile)
        self.assertIsNotNone(chunks)
        self.assertIsNotNone(metadatas)
        self.assertGreater(len(chunks), 0)
        self.assertEqual(len(chunks), len(metadatas))
    
    def test_vector_store(self):
        """Test vector store functionality."""
        # Process and store a document
        chunks, metadatas = process_document(self.company_profile)
        
        # Add text to each metadata for easier retrieval
        for i, metadata in enumerate(metadatas):
            metadata["text"] = chunks[i]
        
        # Store in vector database
        ids = vector_store.add_documents(chunks, metadatas)
        self.assertIsNotNone(ids)
        self.assertGreater(len(ids), 0)
        self.assertEqual(len(ids), len(chunks))
        
        # Search for a query
        query = "When was TechInnovate Solutions founded?"
        texts, metadatas, scores = vector_store.search(query, top_k=2)
        self.assertIsNotNone(texts)
        self.assertIsNotNone(metadatas)
        self.assertIsNotNone(scores)
        self.assertGreater(len(texts), 0)
    
    def test_azure_openai(self):
        """Test Azure OpenAI functionality."""
        # Test generating embeddings
        texts = ["This is a test", "Another test sentence"]
        embeddings = azure_openai_service.generate_embeddings(texts)
        self.assertIsNotNone(embeddings)
        self.assertEqual(len(embeddings), len(texts))
        
        # Test generating chat completion
        system_prompt = "You are a helpful assistant."
        user_message = "What is RAG?"
        response = azure_openai_service.generate_chat_completion(system_prompt, user_message)
        self.assertIsNotNone(response)
        self.assertGreater(len(response), 0)
    
    def test_conversation(self):
        """Test conversation functionality."""
        # Add messages to conversation
        conversation_service.add_message(self.session_id, "user", "Hello")
        conversation_service.add_message(self.session_id, "assistant", "Hi there!")
        
        # Get conversation history
        history = conversation_service.get_conversation_history(self.session_id)
        self.assertIsNotNone(history)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Hi there!")
        
        # Format history for prompt
        formatted_history = conversation_service.format_history_for_prompt(self.session_id)
        self.assertIsNotNone(formatted_history)
        self.assertGreater(len(formatted_history), 0)
    
    def test_rag_query(self):
        """Test RAG query functionality."""
        # Process and store a document
        success = rag_service.process_and_store_document(self.company_profile)
        self.assertTrue(success)
        
        # Perform a RAG query
        query = "When was TechInnovate Solutions founded?"
        result = rag_service.query(query, self.session_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["query"], query)
        self.assertIsNotNone(result["response"])
        self.assertGreater(len(result["response"]), 0)
        self.assertIsNotNone(result["sources"])
    
    def test_profile_matching(self):
        """Test profile matching functionality."""
        # Match profiles to SOW
        matches = rag_service.match_profiles_to_sow(
            profile_file_paths=[self.developer_profile],
            sow_file_path=self.project_sow
        )
        self.assertIsNotNone(matches)
        self.assertGreater(len(matches), 0)
        self.assertIn("match_score", matches[0])
        self.assertIn("matching_skills", matches[0])

if __name__ == "__main__":
    unittest.main()
