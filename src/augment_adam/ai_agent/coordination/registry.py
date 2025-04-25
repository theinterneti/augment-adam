"""
Agent Registry module.

This module provides a registry for tracking available agents and their capabilities.
"""

import uuid
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory


class AgentCapability(Enum):
    """
    Capabilities that agents can have.
    
    This enum defines the capabilities that agents can have, which are used
    for task distribution and coordination.
    """
    
    TEXT_GENERATION = auto()
    CODE_GENERATION = auto()
    CODE_REVIEW = auto()
    INFORMATION_RETRIEVAL = auto()
    REASONING = auto()
    PLANNING = auto()
    EXECUTION = auto()
    COORDINATION = auto()
    MEMORY_MANAGEMENT = auto()
    CONTEXT_MANAGEMENT = auto()
    TOOL_USE = auto()
    CUSTOM = auto()


@dataclass
class Agent:
    """
    Agent in the coordination system.
    
    This class represents an agent in the coordination system, including its
    ID, name, capabilities, and other properties.
    
    Attributes:
        id: Unique identifier for the agent.
        name: The name of the agent.
        capabilities: Set of capabilities the agent has.
        metadata: Additional metadata for the agent.
        is_active: Whether the agent is currently active.
        load: Current load of the agent (0-1).
        tags: List of tags for the agent.
    
    TODO(Issue #8): Add support for agent versioning
    TODO(Issue #8): Implement agent validation
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    capabilities: Set[AgentCapability] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    load: float = 0.0
    tags: List[str] = field(default_factory=list)
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """
        Check if the agent has a specific capability.
        
        Args:
            capability: The capability to check.
            
        Returns:
            True if the agent has the capability, False otherwise.
        """
        return capability in self.capabilities
    
    def add_capability(self, capability: AgentCapability) -> None:
        """
        Add a capability to the agent.
        
        Args:
            capability: The capability to add.
        """
        self.capabilities.add(capability)
    
    def remove_capability(self, capability: AgentCapability) -> bool:
        """
        Remove a capability from the agent.
        
        Args:
            capability: The capability to remove.
            
        Returns:
            True if the capability was removed, False otherwise.
        """
        if capability in self.capabilities:
            self.capabilities.remove(capability)
            return True
        return False
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the agent.
        
        Args:
            tag: The tag to add.
        """
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> bool:
        """
        Remove a tag from the agent.
        
        Args:
            tag: The tag to remove.
            
        Returns:
            True if the tag was removed, False otherwise.
        """
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if the agent has a specific tag.
        
        Args:
            tag: The tag to check.
            
        Returns:
            True if the agent has the tag, False otherwise.
        """
        return tag in self.tags
    
    def update_load(self, load: float) -> None:
        """
        Update the agent's load.
        
        Args:
            load: The new load value (0-1).
        """
        self.load = max(0.0, min(1.0, load))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent to a dictionary.
        
        Returns:
            Dictionary representation of the agent.
        """
        return {
            "id": self.id,
            "name": self.name,
            "capabilities": [capability.name for capability in self.capabilities],
            "metadata": self.metadata,
            "is_active": self.is_active,
            "load": self.load,
            "tags": self.tags,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """
        Create an agent from a dictionary.
        
        Args:
            data: Dictionary representation of the agent.
            
        Returns:
            Agent.
        """
        capabilities = set()
        for capability_name in data.get("capabilities", []):
            try:
                capability = AgentCapability[capability_name]
                capabilities.add(capability)
            except KeyError:
                capabilities.add(AgentCapability.CUSTOM)
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            capabilities=capabilities,
            metadata=data.get("metadata", {}),
            is_active=data.get("is_active", True),
            load=data.get("load", 0.0),
            tags=data.get("tags", []),
        )


@tag("ai_agent.coordination")
class AgentRegistry:
    """
    Registry for tracking available agents and their capabilities.
    
    This class provides a registry for tracking available agents and their
    capabilities, which is used for task distribution and coordination.
    
    Attributes:
        agents: Dictionary of agents, keyed by ID.
        metadata: Additional metadata for the registry.
    
    TODO(Issue #8): Add support for agent persistence
    TODO(Issue #8): Implement agent validation
    """
    
    def __init__(self) -> None:
        """Initialize the agent registry."""
        self.agents: Dict[str, Agent] = {}
        self.metadata: Dict[str, Any] = {}
    
    def register_agent(self, agent: Agent) -> str:
        """
        Register an agent with the registry.
        
        Args:
            agent: The agent to register.
            
        Returns:
            The ID of the registered agent.
        """
        self.agents[agent.id] = agent
        return agent.id
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the registry.
        
        Args:
            agent_id: The ID of the agent to unregister.
            
        Returns:
            True if the agent was unregistered, False otherwise.
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to get.
            
        Returns:
            The agent, or None if it doesn't exist.
        """
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[Agent]:
        """
        Get all agents in the registry.
        
        Returns:
            List of all agents.
        """
        return list(self.agents.values())
    
    def get_active_agents(self) -> List[Agent]:
        """
        Get all active agents in the registry.
        
        Returns:
            List of active agents.
        """
        return [agent for agent in self.agents.values() if agent.is_active]
    
    def get_agents_by_capability(self, capability: AgentCapability) -> List[Agent]:
        """
        Get agents with a specific capability.
        
        Args:
            capability: The capability to filter by.
            
        Returns:
            List of agents with the specified capability.
        """
        return [agent for agent in self.agents.values() if agent.has_capability(capability) and agent.is_active]
    
    def get_agents_by_tag(self, tag: str) -> List[Agent]:
        """
        Get agents with a specific tag.
        
        Args:
            tag: The tag to filter by.
            
        Returns:
            List of agents with the specified tag.
        """
        return [agent for agent in self.agents.values() if agent.has_tag(tag) and agent.is_active]
    
    def get_agents_by_load(self, max_load: float = 1.0) -> List[Agent]:
        """
        Get agents with load below a threshold.
        
        Args:
            max_load: The maximum load threshold.
            
        Returns:
            List of agents with load below the threshold.
        """
        return [agent for agent in self.agents.values() if agent.load <= max_load and agent.is_active]
    
    def update_agent_load(self, agent_id: str, load: float) -> bool:
        """
        Update an agent's load.
        
        Args:
            agent_id: The ID of the agent to update.
            load: The new load value (0-1).
            
        Returns:
            True if the agent's load was updated, False otherwise.
        """
        agent = self.get_agent(agent_id)
        if agent is None:
            return False
        
        agent.update_load(load)
        return True
    
    def set_agent_active(self, agent_id: str, is_active: bool) -> bool:
        """
        Set an agent's active status.
        
        Args:
            agent_id: The ID of the agent to update.
            is_active: The new active status.
            
        Returns:
            True if the agent's status was updated, False otherwise.
        """
        agent = self.get_agent(agent_id)
        if agent is None:
            return False
        
        agent.is_active = is_active
        return True
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the registry.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the registry.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the registry to a dictionary.
        
        Returns:
            Dictionary representation of the registry.
        """
        return {
            "agents": {agent_id: agent.to_dict() for agent_id, agent in self.agents.items()},
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentRegistry':
        """
        Create a registry from a dictionary.
        
        Args:
            data: Dictionary representation of the registry.
            
        Returns:
            Agent registry.
        """
        registry = cls()
        registry.metadata = data.get("metadata", {})
        
        for agent_data in data.get("agents", {}).values():
            agent = Agent.from_dict(agent_data)
            registry.register_agent(agent)
        
        return registry


# Singleton instance
_agent_registry: Optional[AgentRegistry] = None

def get_agent_registry() -> AgentRegistry:
    """
    Get the singleton instance of the agent registry.
    
    Returns:
        The agent registry instance.
    """
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry
