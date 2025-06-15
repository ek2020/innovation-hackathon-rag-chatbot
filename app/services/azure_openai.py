from typing import List, Dict, Any, Optional
import openai
import numpy as np

from app.core.config import settings

class AzureOpenAIService:
    """Service for interacting with Azure OpenAI API."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client."""
        openai.api_type = "azure"
        openai.api_base = settings.AZURE_OPENAI_ENDPOINT
        openai.api_key = settings.AZURE_OPENAI_API_KEY
        openai.api_version = settings.AZURE_OPENAI_API_VERSION
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        # Process in batches to avoid API limits
        batch_size = 16  # Azure OpenAI can handle larger batches, but we'll be conservative
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            
            try:
                print(f"Generating embeddings for {len(batch_texts)} texts")
                response = openai.Embedding.create(
                    input=batch_texts,
                    engine=settings.AZURE_OPENAI_EMBEDDING_MODEL
                )
                
                # Extract embeddings from response
                batch_embeddings = [item["embedding"] for item in response["data"]]
                print(f"Generated embeddings with dimension: {len(batch_embeddings[0])}")
                all_embeddings.extend(batch_embeddings)
                
            except Exception as e:
                print(f"Error generating embeddings: {str(e)}")
                # Return empty embeddings for this batch
                all_embeddings.extend([[0.0] * settings.QDRANT_VECTOR_SIZE] * len(batch_texts))
        
        return all_embeddings
    
    def generate_chat_completion(
        self, 
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> str:
        """
        Generate a chat completion using Azure OpenAI.
        
        Args:
            system_prompt: The system prompt
            user_message: The user message
            conversation_history: Optional conversation history
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response
        """
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = openai.ChatCompletion.create(
                engine=settings.AZURE_OPENAI_CHAT_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"Error generating chat completion: {str(e)}")
            return f"Error: Unable to generate response. {str(e)}"
    
    def contextualize_query(self, query: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Convert follow-up questions into standalone queries.
        
        Args:
            query: The user's query
            conversation_history: The conversation history
            
        Returns:
            Contextualized query
        """
        if not conversation_history:
            return query
            
        system_prompt = """Given a chat history and the latest user question 
        which might reference context in the chat history, formulate a standalone 
        question which can be understood without the chat history. Do NOT answer 
        the question, just reformulate it if needed and otherwise return it as is."""
        
        # Format conversation history for the prompt
        formatted_history = ""
        for msg in conversation_history:
            role = "Human" if msg["role"] == "user" else "Assistant"
            formatted_history += f"{role}: {msg['content']}\n\n"
        
        user_message = f"Chat history:\n{formatted_history}\n\nQuestion:\n{query}"
        
        try:
            response = openai.ChatCompletion.create(
                engine=settings.AZURE_OPENAI_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.0,  # Use low temperature for deterministic output
                max_tokens=100
            )
            
            return response["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"Error contextualizing query: {str(e)}")
            return query  # Fallback to original query
    
    def generate_rag_response(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response using RAG.
        
        Args:
            query: The user's query
            context: The retrieved context
            conversation_history: Optional conversation history
            
        Returns:
            Generated response
        """
        system_prompt = f"""You are a helpful assistant that answers questions based on the provided context.
        Based on the following context and conversation history, please provide a relevant and contextual response.
        If the answer cannot be derived from the context, only use the conversation history or say 
        "I cannot answer this based on the provided information."
        
        Context from documents:
        {context}
        """
        
        return self.generate_chat_completion(
            system_prompt=system_prompt,
            user_message=query,
            conversation_history=conversation_history,
            temperature=0.7
        )

# Create a singleton instance
azure_openai_service = AzureOpenAIService()
