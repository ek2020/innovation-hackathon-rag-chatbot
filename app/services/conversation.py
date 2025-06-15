from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class ConversationService:
    """Service for managing conversation history and sessions."""
    
    def __init__(self):
        """Initialize the conversation service."""
        # In-memory storage for conversations
        # In a production system, this would be a database
        self.conversations = {}
    
    def create_session(self) -> str:
        """
        Create a new conversation session.
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        self.conversations[session_id] = []
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """
        Add a message to the conversation history.
        
        Args:
            session_id: The session ID
            role: The role of the message sender (user or assistant)
            content: The message content
            
        Returns:
            True if successful, False otherwise
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def get_conversation_history(
        self, 
        session_id: str, 
        max_messages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: The session ID
            max_messages: Maximum number of messages to return
            
        Returns:
            List of messages
        """
        if session_id not in self.conversations:
            return []
        
        history = self.conversations[session_id]
        
        if max_messages:
            history = history[-max_messages:]
        
        # Convert to format expected by OpenAI API
        formatted_history = []
        for msg in history:
            formatted_history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return formatted_history
    
    def format_history_for_prompt(self, session_id: str, max_messages: int = 5) -> str:
        """
        Format conversation history for inclusion in prompts.
        
        Args:
            session_id: The session ID
            max_messages: Maximum number of messages to include
            
        Returns:
            Formatted conversation history
        """
        history = self.get_conversation_history(session_id, max_messages)
        formatted_history = ""
        
        for msg in history:
            role = "Human" if msg["role"] == "user" else "Assistant"
            formatted_history += f"{role}: {msg['content']}\n\n"
        
        return formatted_history.strip()
    
    def clear_conversation(self, session_id: str) -> bool:
        """
        Clear conversation history for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            True if successful, False otherwise
        """
        if session_id in self.conversations:
            self.conversations[session_id] = []
            return True
        
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a conversation session.
        
        Args:
            session_id: The session ID
            
        Returns:
            True if successful, False otherwise
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        
        return False
    
    def get_all_sessions(self) -> List[str]:
        """
        Get all session IDs.
        
        Returns:
            List of session IDs
        """
        return list(self.conversations.keys())

# Create a singleton instance
conversation_service = ConversationService()
