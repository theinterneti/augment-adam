"""Core assistant implementation for Dukat.

This module provides the main Assistant class that integrates
the model manager, memory system, and other components.

Version: 0.1.0
Created: 2025-04-22
"""

from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime
import uuid

import dspy

from dukat.core.model_manager import get_model_manager, ModelManager
from dukat.core.memory import get_memory, Memory

logger = logging.getLogger(__name__)


class Assistant:
    """Main assistant class for Dukat.
    
    This class integrates the model manager, memory system, and other
    components to provide a complete assistant experience.
    
    Attributes:
        model_manager: The model manager instance.
        memory: The memory system instance.
        conversation_id: The ID of the current conversation.
    """
    
    def __init__(
        self,
        model_name: str = "llama3:8b",
        ollama_host: str = "http://localhost:11434",
        persist_dir: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ):
        """Initialize the assistant.
        
        Args:
            model_name: The name of the model to use.
            ollama_host: The host address for the Ollama API.
            persist_dir: Directory to persist memory data.
            conversation_id: The ID of the conversation to continue.
        """
        # Initialize components
        self.model_manager = get_model_manager(model_name, ollama_host)
        self.memory = get_memory(persist_dir)
        
        # Set or generate conversation ID
        self.conversation_id = conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
        
        # Create DSPy modules
        self.chat_module = self.model_manager.create_module(
            "history, question -> response"
        )
        
        logger.info(f"Initialized Assistant with conversation_id: {self.conversation_id}")
    
    def ask(
        self,
        question: str,
        include_history: bool = True,
        max_history_items: int = 5,
    ) -> str:
        """Ask a question to the assistant.
        
        Args:
            question: The question to ask.
            include_history: Whether to include conversation history.
            max_history_items: Maximum number of history items to include.
            
        Returns:
            The assistant's response.
        """
        logger.info(f"Received question: {question[:50]}...")
        
        # Store the question in memory
        self.memory.add(
            text=question,
            metadata={
                "type": "user_message",
                "conversation_id": self.conversation_id,
            },
        )
        
        # Get conversation history if needed
        history = ""
        if include_history:
            history_items = self.memory.retrieve(
                query="",
                n_results=max_history_items * 2,  # Get more to filter
                filter_metadata={"conversation_id": self.conversation_id},
            )
            
            # Format history items
            formatted_items = []
            for item in history_items:
                item_type = item["metadata"].get("type", "")
                if item_type == "user_message":
                    formatted_items.append(f"User: {item['text']}")
                elif item_type == "assistant_message":
                    formatted_items.append(f"Assistant: {item['text']}")
            
            history = "\\n".join(formatted_items[-max_history_items*2:])
        
        # Generate response using DSPy
        try:
            prediction = self.chat_module(history=history, question=question)
            response = prediction.response
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            response = f"I'm sorry, I encountered an error: {str(e)}"
        
        # Store the response in memory
        self.memory.add(
            text=response,
            metadata={
                "type": "assistant_message",
                "conversation_id": self.conversation_id,
            },
        )
        
        logger.info(f"Generated response: {response[:50]}...")
        return response
    
    def new_conversation(self) -> str:
        """Start a new conversation.
        
        Returns:
            The ID of the new conversation.
        """
        self.conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        logger.info(f"Started new conversation with ID: {self.conversation_id}")
        return self.conversation_id
    
    def get_conversation_history(
        self,
        max_items: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get the history of the current conversation.
        
        Args:
            max_items: Maximum number of history items to return.
            
        Returns:
            A list of conversation messages with metadata.
        """
        history_items = self.memory.retrieve(
            query="",
            n_results=max_items * 2,  # Get more to filter
            filter_metadata={"conversation_id": self.conversation_id},
        )
        
        # Format and sort history items
        formatted_items = []
        for item in history_items:
            formatted_items.append({
                "id": item["id"],
                "text": item["text"],
                "type": item["metadata"].get("type", ""),
                "timestamp": item["metadata"].get("timestamp", ""),
            })
        
        # Sort by timestamp
        formatted_items.sort(key=lambda x: x["timestamp"])
        
        return formatted_items[-max_items:]
