"""Agent implementation for Augment Adam.

This module contains the Agent class, which is the main interface for
interacting with Augment Adam.
"""

from typing import Any, Dict, List, Optional, Union

from augment_adam.memory import BaseMemory


class Agent:
    """Agent class for Augment Adam.

    This class provides the main interface for interacting with Augment Adam.
    It handles the communication with the underlying model and memory systems.

    Attributes:
        name: The name of the agent.
        memory: The memory system used by the agent.
        model_name: The name of the model used by the agent.
        model_params: Additional parameters for the model.
    """

    def __init__(
        self,
        name: str = "Augment Adam",
        memory: Optional[BaseMemory] = None,
        model_name: str = "default",
        model_params: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the agent.

        Args:
            name: The name of the agent.
            memory: The memory system to use. If None, a default memory system will be used.
            model_name: The name of the model to use.
            model_params: Additional parameters for the model.
        """
        self.name = name
        self.memory = memory
        self.model_name = model_name
        self.model_params = model_params or {}

    def run(self, input_text: str) -> str:
        """Run the agent on the given input.

        Args:
            input_text: The input text to process.

        Returns:
            The agent's response.
        """
        # This is a placeholder implementation
        return f"Agent {self.name} received: {input_text}"

    def add_to_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add text to the agent's memory.

        Args:
            text: The text to add to memory.
            metadata: Additional metadata for the memory entry.
        """
        if self.memory:
            self.memory.add(text, metadata)

    def search_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search the agent's memory.

        Args:
            query: The search query.
            limit: The maximum number of results to return.

        Returns:
            A list of memory entries matching the query.
        """
        if self.memory:
            return self.memory.search(query, limit)
        return []
