"""
Task module for agent coordination.

This module provides classes for representing and distributing tasks among agents.
"""

import uuid
import time
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.ai_agent.coordination.registry import Agent, AgentCapability, AgentRegistry, get_agent_registry


class TaskStatus(Enum):
    """
    Status of a task.
    
    This enum defines the possible statuses of a task, including pending,
    assigned, in progress, completed, failed, and cancelled.
    """
    
    PENDING = auto()
    ASSIGNED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class TaskPriority(Enum):
    """
    Priority of a task.
    
    This enum defines the possible priorities of a task, which are used
    for task queue ordering.
    """
    
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class TaskResult:
    """
    Result of a completed task.
    
    This class represents the result of a completed task, including the
    output, status, and other properties.
    
    Attributes:
        task_id: ID of the task.
        agent_id: ID of the agent that completed the task.
        output: The output of the task.
        status: The status of the task.
        timestamp: When the result was created.
        metadata: Additional metadata for the result.
        error: Error message if the task failed.
    
    TODO(Issue #8): Add support for result validation
    """
    
    task_id: str = ""
    agent_id: str = ""
    output: Any = None
    status: TaskStatus = TaskStatus.COMPLETED
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def is_successful(self) -> bool:
        """
        Check if the task was completed successfully.
        
        Returns:
            True if the task was completed successfully, False otherwise.
        """
        return self.status == TaskStatus.COMPLETED and self.error is None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task result to a dictionary.
        
        Returns:
            Dictionary representation of the task result.
        """
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "output": self.output,
            "status": self.status.name,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "error": self.error,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskResult':
        """
        Create a task result from a dictionary.
        
        Args:
            data: Dictionary representation of the task result.
            
        Returns:
            Task result.
        """
        # Convert status from string to enum
        status = data.get("status", TaskStatus.COMPLETED.name)
        if isinstance(status, str):
            try:
                status = TaskStatus[status]
            except KeyError:
                status = TaskStatus.COMPLETED
        
        return cls(
            task_id=data.get("task_id", ""),
            agent_id=data.get("agent_id", ""),
            output=data.get("output"),
            status=status,
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {}),
            error=data.get("error"),
        )


@dataclass
class Task:
    """
    Task for agents to perform.
    
    This class represents a task for agents to perform, including its
    input, requirements, and other properties.
    
    Attributes:
        id: Unique identifier for the task.
        name: The name of the task.
        description: Description of the task.
        input: The input for the task.
        required_capabilities: Set of capabilities required to perform the task.
        priority: The priority of the task.
        status: The status of the task.
        assigned_agent_id: ID of the agent assigned to the task.
        parent_task_id: ID of the parent task, if this is a subtask.
        subtask_ids: List of subtask IDs.
        created_at: When the task was created.
        updated_at: When the task was last updated.
        deadline: When the task must be completed by, if applicable.
        metadata: Additional metadata for the task.
        result: The result of the task, if completed.
        tags: List of tags for the task.
    
    TODO(Issue #8): Add support for task versioning
    TODO(Issue #8): Implement task validation
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    input: Any = None
    required_capabilities: Set[AgentCapability] = field(default_factory=set)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    subtask_ids: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[TaskResult] = None
    tags: List[str] = field(default_factory=list)
    
    def is_assigned(self) -> bool:
        """
        Check if the task is assigned to an agent.
        
        Returns:
            True if the task is assigned, False otherwise.
        """
        return self.assigned_agent_id is not None and self.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
    
    def is_completed(self) -> bool:
        """
        Check if the task is completed.
        
        Returns:
            True if the task is completed, False otherwise.
        """
        return self.status == TaskStatus.COMPLETED and self.result is not None
    
    def is_failed(self) -> bool:
        """
        Check if the task failed.
        
        Returns:
            True if the task failed, False otherwise.
        """
        return self.status == TaskStatus.FAILED
    
    def is_cancelled(self) -> bool:
        """
        Check if the task is cancelled.
        
        Returns:
            True if the task is cancelled, False otherwise.
        """
        return self.status == TaskStatus.CANCELLED
    
    def is_overdue(self) -> bool:
        """
        Check if the task is overdue.
        
        Returns:
            True if the task is overdue, False otherwise.
        """
        if self.deadline is None:
            return False
        
        return time.time() > self.deadline
    
    def has_subtasks(self) -> bool:
        """
        Check if the task has subtasks.
        
        Returns:
            True if the task has subtasks, False otherwise.
        """
        return len(self.subtask_ids) > 0
    
    def add_subtask(self, subtask_id: str) -> None:
        """
        Add a subtask to the task.
        
        Args:
            subtask_id: The ID of the subtask to add.
        """
        if subtask_id not in self.subtask_ids:
            self.subtask_ids.append(subtask_id)
            self.updated_at = time.time()
    
    def remove_subtask(self, subtask_id: str) -> bool:
        """
        Remove a subtask from the task.
        
        Args:
            subtask_id: The ID of the subtask to remove.
            
        Returns:
            True if the subtask was removed, False otherwise.
        """
        if subtask_id in self.subtask_ids:
            self.subtask_ids.remove(subtask_id)
            self.updated_at = time.time()
            return True
        return False
    
    def assign(self, agent_id: str) -> None:
        """
        Assign the task to an agent.
        
        Args:
            agent_id: The ID of the agent to assign the task to.
        """
        self.assigned_agent_id = agent_id
        self.status = TaskStatus.ASSIGNED
        self.updated_at = time.time()
    
    def start(self) -> None:
        """
        Mark the task as in progress.
        """
        if self.status == TaskStatus.ASSIGNED:
            self.status = TaskStatus.IN_PROGRESS
            self.updated_at = time.time()
    
    def complete(self, result: TaskResult) -> None:
        """
        Mark the task as completed with a result.
        
        Args:
            result: The result of the task.
        """
        self.result = result
        self.status = TaskStatus.COMPLETED
        self.updated_at = time.time()
    
    def fail(self, error: str) -> None:
        """
        Mark the task as failed with an error.
        
        Args:
            error: The error message.
        """
        if self.result is None:
            self.result = TaskResult(
                task_id=self.id,
                agent_id=self.assigned_agent_id or "",
                status=TaskStatus.FAILED,
                error=error
            )
        else:
            self.result.status = TaskStatus.FAILED
            self.result.error = error
        
        self.status = TaskStatus.FAILED
        self.updated_at = time.time()
    
    def cancel(self) -> None:
        """
        Mark the task as cancelled.
        """
        self.status = TaskStatus.CANCELLED
        self.updated_at = time.time()
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the task.
        
        Args:
            tag: The tag to add.
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = time.time()
    
    def remove_tag(self, tag: str) -> bool:
        """
        Remove a tag from the task.
        
        Args:
            tag: The tag to remove.
            
        Returns:
            True if the tag was removed, False otherwise.
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = time.time()
            return True
        return False
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if the task has a specific tag.
        
        Args:
            tag: The tag to check.
            
        Returns:
            True if the task has the tag, False otherwise.
        """
        return tag in self.tags
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary.
        
        Returns:
            Dictionary representation of the task.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "input": self.input,
            "required_capabilities": [capability.name for capability in self.required_capabilities],
            "priority": self.priority.name,
            "status": self.status.name,
            "assigned_agent_id": self.assigned_agent_id,
            "parent_task_id": self.parent_task_id,
            "subtask_ids": self.subtask_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deadline": self.deadline,
            "metadata": self.metadata,
            "result": self.result.to_dict() if self.result is not None else None,
            "tags": self.tags,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        Create a task from a dictionary.
        
        Args:
            data: Dictionary representation of the task.
            
        Returns:
            Task.
        """
        # Convert required_capabilities from strings to enums
        required_capabilities = set()
        for capability_name in data.get("required_capabilities", []):
            try:
                capability = AgentCapability[capability_name]
                required_capabilities.add(capability)
            except KeyError:
                required_capabilities.add(AgentCapability.CUSTOM)
        
        # Convert priority from string to enum
        priority = data.get("priority", TaskPriority.NORMAL.name)
        if isinstance(priority, str):
            try:
                priority = TaskPriority[priority]
            except KeyError:
                priority = TaskPriority.NORMAL
        
        # Convert status from string to enum
        status = data.get("status", TaskStatus.PENDING.name)
        if isinstance(status, str):
            try:
                status = TaskStatus[status]
            except KeyError:
                status = TaskStatus.PENDING
        
        # Convert result from dictionary to TaskResult
        result = None
        if data.get("result") is not None:
            result = TaskResult.from_dict(data["result"])
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            input=data.get("input"),
            required_capabilities=required_capabilities,
            priority=priority,
            status=status,
            assigned_agent_id=data.get("assigned_agent_id"),
            parent_task_id=data.get("parent_task_id"),
            subtask_ids=data.get("subtask_ids", []),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            deadline=data.get("deadline"),
            metadata=data.get("metadata", {}),
            result=result,
            tags=data.get("tags", []),
        )


@tag("ai_agent.coordination")
class TaskDistributor:
    """
    Base class for task distributors.
    
    This class defines the interface for task distributors, which assign
    tasks to agents based on various strategies.
    
    Attributes:
        name: The name of the task distributor.
        registry: The agent registry to use for task distribution.
        metadata: Additional metadata for the distributor.
    
    TODO(Issue #8): Add support for distributor validation
    TODO(Issue #8): Implement distributor analytics
    """
    
    def __init__(self, name: str, registry: Optional[AgentRegistry] = None) -> None:
        """
        Initialize the task distributor.
        
        Args:
            name: The name of the task distributor.
            registry: The agent registry to use for task distribution.
        """
        self.name = name
        self.registry = registry or get_agent_registry()
        self.metadata: Dict[str, Any] = {}
    
    def distribute(self, task: Task) -> Optional[str]:
        """
        Distribute a task to an agent.
        
        Args:
            task: The task to distribute.
            
        Returns:
            The ID of the agent assigned to the task, or None if no agent was assigned.
        """
        raise NotImplementedError("Subclasses must implement distribute")
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the distributor.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the distributor.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("ai_agent.coordination")
class RoundRobinDistributor(TaskDistributor):
    """
    Task distributor that assigns tasks in a round-robin fashion.
    
    This class implements a task distributor that assigns tasks to agents
    in a round-robin fashion, cycling through all available agents.
    
    Attributes:
        name: The name of the task distributor.
        registry: The agent registry to use for task distribution.
        metadata: Additional metadata for the distributor.
        last_agent_index: Index of the last agent assigned a task.
    
    TODO(Issue #8): Add support for distributor validation
    TODO(Issue #8): Implement distributor analytics
    """
    
    def __init__(self, name: str = "round_robin_distributor", registry: Optional[AgentRegistry] = None) -> None:
        """
        Initialize the round-robin task distributor.
        
        Args:
            name: The name of the task distributor.
            registry: The agent registry to use for task distribution.
        """
        super().__init__(name, registry)
        self.last_agent_index = -1
    
    def distribute(self, task: Task) -> Optional[str]:
        """
        Distribute a task to an agent in a round-robin fashion.
        
        Args:
            task: The task to distribute.
            
        Returns:
            The ID of the agent assigned to the task, or None if no agent was assigned.
        """
        # Get active agents
        agents = self.registry.get_active_agents()
        
        # If there are no active agents, return None
        if not agents:
            return None
        
        # Filter agents by required capabilities
        if task.required_capabilities:
            agents = [agent for agent in agents if all(agent.has_capability(capability) for capability in task.required_capabilities)]
            
            # If there are no agents with the required capabilities, return None
            if not agents:
                return None
        
        # Get the next agent in the rotation
        self.last_agent_index = (self.last_agent_index + 1) % len(agents)
        agent = agents[self.last_agent_index]
        
        # Assign the task to the agent
        task.assign(agent.id)
        
        # Update the agent's load
        agent.update_load(min(1.0, agent.load + 0.1))
        
        return agent.id


@tag("ai_agent.coordination")
class CapabilityBasedDistributor(TaskDistributor):
    """
    Task distributor that assigns tasks based on agent capabilities.
    
    This class implements a task distributor that assigns tasks to agents
    based on their capabilities, choosing the agent with the most matching capabilities.
    
    Attributes:
        name: The name of the task distributor.
        registry: The agent registry to use for task distribution.
        metadata: Additional metadata for the distributor.
    
    TODO(Issue #8): Add support for distributor validation
    TODO(Issue #8): Implement distributor analytics
    """
    
    def __init__(self, name: str = "capability_based_distributor", registry: Optional[AgentRegistry] = None) -> None:
        """
        Initialize the capability-based task distributor.
        
        Args:
            name: The name of the task distributor.
            registry: The agent registry to use for task distribution.
        """
        super().__init__(name, registry)
    
    def distribute(self, task: Task) -> Optional[str]:
        """
        Distribute a task to an agent based on capabilities.
        
        Args:
            task: The task to distribute.
            
        Returns:
            The ID of the agent assigned to the task, or None if no agent was assigned.
        """
        # Get active agents
        agents = self.registry.get_active_agents()
        
        # If there are no active agents, return None
        if not agents:
            return None
        
        # Filter agents by required capabilities
        if task.required_capabilities:
            agents = [agent for agent in agents if all(agent.has_capability(capability) for capability in task.required_capabilities)]
            
            # If there are no agents with the required capabilities, return None
            if not agents:
                return None
        
        # If there are no required capabilities, just pick the first agent
        if not task.required_capabilities:
            agent = agents[0]
            task.assign(agent.id)
            agent.update_load(min(1.0, agent.load + 0.1))
            return agent.id
        
        # Score agents based on matching capabilities
        best_agent = None
        best_score = -1
        
        for agent in agents:
            # Count matching capabilities
            score = sum(1 for capability in task.required_capabilities if agent.has_capability(capability))
            
            # Adjust score based on agent load
            score = score * (1.0 - agent.load)
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        # If no agent was found, return None
        if best_agent is None:
            return None
        
        # Assign the task to the best agent
        task.assign(best_agent.id)
        
        # Update the agent's load
        best_agent.update_load(min(1.0, best_agent.load + 0.1))
        
        return best_agent.id


@tag("ai_agent.coordination")
class LoadBalancedDistributor(TaskDistributor):
    """
    Task distributor that assigns tasks based on agent load.
    
    This class implements a task distributor that assigns tasks to agents
    based on their current load, choosing the agent with the lowest load.
    
    Attributes:
        name: The name of the task distributor.
        registry: The agent registry to use for task distribution.
        metadata: Additional metadata for the distributor.
    
    TODO(Issue #8): Add support for distributor validation
    TODO(Issue #8): Implement distributor analytics
    """
    
    def __init__(self, name: str = "load_balanced_distributor", registry: Optional[AgentRegistry] = None) -> None:
        """
        Initialize the load-balanced task distributor.
        
        Args:
            name: The name of the task distributor.
            registry: The agent registry to use for task distribution.
        """
        super().__init__(name, registry)
    
    def distribute(self, task: Task) -> Optional[str]:
        """
        Distribute a task to an agent based on load.
        
        Args:
            task: The task to distribute.
            
        Returns:
            The ID of the agent assigned to the task, or None if no agent was assigned.
        """
        # Get active agents
        agents = self.registry.get_active_agents()
        
        # If there are no active agents, return None
        if not agents:
            return None
        
        # Filter agents by required capabilities
        if task.required_capabilities:
            agents = [agent for agent in agents if all(agent.has_capability(capability) for capability in task.required_capabilities)]
            
            # If there are no agents with the required capabilities, return None
            if not agents:
                return None
        
        # Find the agent with the lowest load
        best_agent = min(agents, key=lambda agent: agent.load)
        
        # Assign the task to the agent
        task.assign(best_agent.id)
        
        # Update the agent's load
        best_agent.update_load(min(1.0, best_agent.load + 0.1))
        
        return best_agent.id
