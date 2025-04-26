"""
Mock implementation of the Task class for testing.

This module contains a mock implementation of the Task class that can be used
for testing without depending on the actual implementation.
"""

import time
import uuid
from enum import Enum, auto
from typing import Optional, List, Dict, Any, Set


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = auto()
    ASSIGNED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class TaskPriority(Enum):
    """Priority of a task."""
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    URGENT = auto()


class AgentCapability(Enum):
    """Capabilities that agents can have."""
    REASONING = auto()
    PLANNING = auto()
    TEXT_GENERATION = auto()
    SUMMARIZATION = auto()
    CODE_GENERATION = auto()
    SEARCH = auto()
    MATH = auto()
    CUSTOM = auto()


class TaskResult:
    """Result of a task execution."""
    
    def __init__(
        self,
        task_id: str,
        agent_id: Optional[str] = None,
        output: Any = None,
        status: TaskStatus = TaskStatus.COMPLETED,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Initialize the task result."""
        self.task_id = task_id
        self.agent_id = agent_id
        self.output = output
        self.status = status
        self.timestamp = timestamp or time.time()
        self.metadata = metadata or {}
        self.error = error
    
    def is_successful(self) -> bool:
        """Check if the task was successful."""
        return self.status == TaskStatus.COMPLETED and self.error is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task result to a dictionary."""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "output": self.output,
            "status": self.status.name,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskResult':
        """Create a task result from a dictionary."""
        status_str = data.get("status", TaskStatus.COMPLETED.name)
        if isinstance(status_str, str):
            try:
                status = TaskStatus[status_str]
            except KeyError:
                status = TaskStatus.COMPLETED
        else:
            status = status_str
        
        return cls(
            task_id=data.get("task_id", ""),
            agent_id=data.get("agent_id"),
            output=data.get("output"),
            status=status,
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {}),
            error=data.get("error")
        )


class Task:
    """Task to be executed by an agent."""
    
    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        description: str = "",
        input: Any = None,
        required_capabilities: Optional[Set[AgentCapability]] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        status: TaskStatus = TaskStatus.PENDING,
        assigned_agent_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        subtask_ids: Optional[List[str]] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        deadline: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        result: Optional[TaskResult] = None,
        tags: Optional[List[str]] = None
    ):
        """Initialize the task."""
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.input = input
        self.required_capabilities = required_capabilities or set()
        self.priority = priority
        self.status = status
        self.assigned_agent_id = assigned_agent_id
        self.parent_task_id = parent_task_id
        self.subtask_ids = subtask_ids or []
        self.created_at = created_at or time.time()
        self.updated_at = updated_at or self.created_at
        self.deadline = deadline
        self.metadata = metadata or {}
        self.result = result
        self.tags = tags or []
    
    def is_assigned(self) -> bool:
        """Check if the task is assigned to an agent."""
        return (
            self.assigned_agent_id is not None and
            self.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
        )
    
    def is_completed(self) -> bool:
        """Check if the task is completed."""
        return (
            self.status == TaskStatus.COMPLETED and
            self.result is not None
        )
    
    def is_failed(self) -> bool:
        """Check if the task failed."""
        return self.status == TaskStatus.FAILED
    
    def is_cancelled(self) -> bool:
        """Check if the task is cancelled."""
        return self.status == TaskStatus.CANCELLED
    
    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        if self.deadline is None:
            return False
        
        return time.time() > self.deadline
    
    def has_subtasks(self) -> bool:
        """Check if the task has subtasks."""
        return len(self.subtask_ids) > 0
    
    def assign(self, agent_id: str) -> None:
        """Assign the task to an agent."""
        self.assigned_agent_id = agent_id
        self.status = TaskStatus.ASSIGNED
        self.updated_at = time.time()
    
    def start(self) -> None:
        """Start the task."""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = time.time()
    
    def complete(self, result: TaskResult) -> None:
        """Complete the task with a result."""
        self.result = result
        self.status = TaskStatus.COMPLETED
        self.updated_at = time.time()
    
    def fail(self, error: str) -> None:
        """Fail the task with an error."""
        if self.result is None:
            self.result = TaskResult(
                task_id=self.id,
                status=TaskStatus.FAILED,
                error=error
            )
        else:
            self.result.status = TaskStatus.FAILED
            self.result.error = error
        
        self.status = TaskStatus.FAILED
        self.updated_at = time.time()
    
    def cancel(self) -> None:
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
        self.updated_at = time.time()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the task."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = time.time()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the task."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "input": self.input,
            "required_capabilities": [cap.name for cap in self.required_capabilities],
            "priority": self.priority.name,
            "status": self.status.name,
            "assigned_agent_id": self.assigned_agent_id,
            "parent_task_id": self.parent_task_id,
            "subtask_ids": self.subtask_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deadline": self.deadline,
            "metadata": self.metadata,
            "result": self.result.to_dict() if self.result else None,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create a task from a dictionary."""
        # Convert required_capabilities from strings to enum values
        required_capabilities = set()
        for cap_str in data.get("required_capabilities", []):
            if isinstance(cap_str, str):
                try:
                    required_capabilities.add(AgentCapability[cap_str])
                except KeyError:
                    pass
            else:
                required_capabilities.add(cap_str)
        
        # Convert priority from string to enum value
        priority_str = data.get("priority", TaskPriority.NORMAL.name)
        if isinstance(priority_str, str):
            try:
                priority = TaskPriority[priority_str]
            except KeyError:
                priority = TaskPriority.NORMAL
        else:
            priority = priority_str
        
        # Convert status from string to enum value
        status_str = data.get("status", TaskStatus.PENDING.name)
        if isinstance(status_str, str):
            try:
                status = TaskStatus[status_str]
            except KeyError:
                status = TaskStatus.PENDING
        else:
            status = status_str
        
        # Convert result from dictionary to TaskResult
        result_dict = data.get("result")
        result = TaskResult.from_dict(result_dict) if result_dict else None
        
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            input=data.get("input"),
            required_capabilities=required_capabilities,
            priority=priority,
            status=status,
            assigned_agent_id=data.get("assigned_agent_id"),
            parent_task_id=data.get("parent_task_id"),
            subtask_ids=data.get("subtask_ids", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            deadline=data.get("deadline"),
            metadata=data.get("metadata", {}),
            result=result,
            tags=data.get("tags", [])
        )
