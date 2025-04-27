"""
Agent Coordinator module.

This module provides a coordinator for managing agent coordination, including
task distribution, communication, and result aggregation.
"""

import uuid
import time
import threading
import queue
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, Tuple
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.ai_agent.coordination.registry import (
    Agent, AgentCapability, AgentRegistry, get_agent_registry
)
from augment_adam.ai_agent.coordination.communication import (
    AgentMessage, MessageType, MessagePriority, AgentCommunicationChannel,
    DirectCommunicationChannel, BroadcastCommunicationChannel, TopicCommunicationChannel
)
from augment_adam.ai_agent.coordination.task import (
    Task, TaskStatus, TaskPriority, TaskResult, TaskDistributor,
    RoundRobinDistributor, CapabilityBasedDistributor, LoadBalancedDistributor
)
from augment_adam.ai_agent.coordination.aggregation import (
    ResultAggregator, SimpleAggregator, WeightedAggregator, VotingAggregator
)
from augment_adam.ai_agent.coordination.patterns import (
    CoordinationPattern, HierarchicalPattern, PeerToPeerPattern, MarketBasedPattern
)


@tag("ai_agent.coordination")
class AgentCoordinator:
    """
    Coordinator for managing agent coordination.

    This class provides a coordinator for managing agent coordination, including
    task distribution, communication, and result aggregation.

    Attributes:
        name: The name of the coordinator.
        registry: The agent registry to use for coordination.
        channels: Dictionary of communication channels, keyed by name.
        distributors: Dictionary of task distributors, keyed by name.
        aggregators: Dictionary of result aggregators, keyed by name.
        patterns: Dictionary of coordination patterns, keyed by name.
        tasks: Dictionary of tasks, keyed by ID.
        results: Dictionary of task results, keyed by task ID.
        metadata: Additional metadata for the coordinator.

    TODO(Issue #8): Add support for coordinator persistence
    TODO(Issue #8): Implement coordinator validation
    """

    def __init__(self, name: str = "agent_coordinator", registry: Optional[AgentRegistry] = None) -> None:
        """
        Initialize the agent coordinator.

        Args:
            name: The name of the coordinator.
            registry: The agent registry to use for coordination.
        """
        self.name = name
        self.registry = registry or get_agent_registry()
        self.channels: Dict[str, AgentCommunicationChannel] = {}
        self.distributors: Dict[str, TaskDistributor] = {}
        self.aggregators: Dict[str, ResultAggregator] = {}
        self.patterns: Dict[str, CoordinationPattern] = {}
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, TaskResult] = {}
        self.metadata: Dict[str, Any] = {}

        # Initialize default components
        self._init_default_components()

    def _init_default_components(self) -> None:
        """Initialize default components for the coordinator."""
        # Create default communication channels
        self.register_channel(DirectCommunicationChannel())
        self.register_channel(BroadcastCommunicationChannel())
        self.register_channel(TopicCommunicationChannel())

        # Create default task distributors
        self.register_distributor(RoundRobinDistributor())
        self.register_distributor(CapabilityBasedDistributor())
        self.register_distributor(LoadBalancedDistributor())

        # Create default result aggregators
        self.register_aggregator(SimpleAggregator())
        self.register_aggregator(WeightedAggregator())
        self.register_aggregator(VotingAggregator())

        # Create default coordination patterns
        self.register_pattern(HierarchicalPattern())
        self.register_pattern(PeerToPeerPattern())
        self.register_pattern(MarketBasedPattern())

    def register_channel(self, channel: AgentCommunicationChannel) -> None:
        """
        Register a communication channel with the coordinator.

        Args:
            channel: The communication channel to register.
        """
        self.channels[channel.name] = channel

    def unregister_channel(self, name: str) -> bool:
        """
        Unregister a communication channel from the coordinator.

        Args:
            name: The name of the communication channel to unregister.

        Returns:
            True if the channel was unregistered, False otherwise.
        """
        if name in self.channels:
            del self.channels[name]
            return True
        return False

    def get_channel(self, name: str) -> Optional[AgentCommunicationChannel]:
        """
        Get a communication channel by name.

        Args:
            name: The name of the communication channel.

        Returns:
            The communication channel, or None if it doesn't exist.
        """
        return self.channels.get(name)

    def register_distributor(self, distributor: TaskDistributor) -> None:
        """
        Register a task distributor with the coordinator.

        Args:
            distributor: The task distributor to register.
        """
        self.distributors[distributor.name] = distributor

    def unregister_distributor(self, name: str) -> bool:
        """
        Unregister a task distributor from the coordinator.

        Args:
            name: The name of the task distributor to unregister.

        Returns:
            True if the distributor was unregistered, False otherwise.
        """
        if name in self.distributors:
            del self.distributors[name]
            return True
        return False

    def get_distributor(self, name: str) -> Optional[TaskDistributor]:
        """
        Get a task distributor by name.

        Args:
            name: The name of the task distributor.

        Returns:
            The task distributor, or None if it doesn't exist.
        """
        return self.distributors.get(name)

    def register_aggregator(self, aggregator: ResultAggregator) -> None:
        """
        Register a result aggregator with the coordinator.

        Args:
            aggregator: The result aggregator to register.
        """
        self.aggregators[aggregator.name] = aggregator

    def unregister_aggregator(self, name: str) -> bool:
        """
        Unregister a result aggregator from the coordinator.

        Args:
            name: The name of the result aggregator to unregister.

        Returns:
            True if the aggregator was unregistered, False otherwise.
        """
        if name in self.aggregators:
            del self.aggregators[name]
            return True
        return False

    def get_aggregator(self, name: str) -> Optional[ResultAggregator]:
        """
        Get a result aggregator by name.

        Args:
            name: The name of the result aggregator.

        Returns:
            The result aggregator, or None if it doesn't exist.
        """
        return self.aggregators.get(name)

    def register_pattern(self, pattern: CoordinationPattern) -> None:
        """
        Register a coordination pattern with the coordinator.

        Args:
            pattern: The coordination pattern to register.
        """
        self.patterns[pattern.name] = pattern

    def unregister_pattern(self, name: str) -> bool:
        """
        Unregister a coordination pattern from the coordinator.

        Args:
            name: The name of the coordination pattern to unregister.

        Returns:
            True if the pattern was unregistered, False otherwise.
        """
        if name in self.patterns:
            del self.patterns[name]
            return True
        return False

    def get_pattern(self, name: str) -> Optional[CoordinationPattern]:
        """
        Get a coordination pattern by name.

        Args:
            name: The name of the coordination pattern.

        Returns:
            The coordination pattern, or None if it doesn't exist.
        """
        return self.patterns.get(name)

    def create_task(
        self,
        name: str,
        description: str,
        input: Any,
        required_capabilities: Optional[List[AgentCapability]] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        parent_task_id: Optional[str] = None,
        deadline: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create a new task.

        Args:
            name: The name of the task.
            description: Description of the task.
            input: The input for the task.
            required_capabilities: List of capabilities required to perform the task.
            priority: The priority of the task.
            parent_task_id: ID of the parent task, if this is a subtask.
            deadline: When the task must be completed by, if applicable.
            metadata: Additional metadata for the task.
            tags: List of tags for the task.

        Returns:
            The ID of the created task.
        """
        # Create the task
        task = Task(
            name=name,
            description=description,
            input=input,
            required_capabilities=set(required_capabilities or []),
            priority=priority,
            parent_task_id=parent_task_id,
            deadline=deadline,
            metadata=metadata or {},
            tags=tags or []
        )

        # Add the task to the dictionary
        self.tasks[task.id] = task

        # If this is a subtask, add it to the parent task
        if parent_task_id is not None:
            parent_task = self.get_task(parent_task_id)
            if parent_task is not None:
                parent_task.add_subtask(task.id)

        return task.id

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: The ID of the task to get.

        Returns:
            The task, or None if it doesn't exist.
        """
        return self.tasks.get(task_id)

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Get tasks by status.

        Args:
            status: The status to filter by.

        Returns:
            List of tasks with the specified status.
        """
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_agent(self, agent_id: str) -> List[Task]:
        """
        Get tasks assigned to an agent.

        Args:
            agent_id: The ID of the agent.

        Returns:
            List of tasks assigned to the agent.
        """
        return [task for task in self.tasks.values() if task.assigned_agent_id == agent_id]

    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """
        Get tasks with a specific tag.

        Args:
            tag: The tag to filter by.

        Returns:
            List of tasks with the specified tag.
        """
        return [task for task in self.tasks.values() if tag in task.tags]

    def get_subtasks(self, task_id: str) -> List[Task]:
        """
        Get subtasks of a task.

        Args:
            task_id: The ID of the parent task.

        Returns:
            List of subtasks.
        """
        task = self.get_task(task_id)
        if task is None:
            return []

        return [self.get_task(subtask_id) for subtask_id in task.subtask_ids if self.get_task(subtask_id) is not None]

    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """
        Get the result of a task.

        Args:
            task_id: The ID of the task.

        Returns:
            The task result, or None if the task doesn't exist or hasn't been completed.
        """
        # Check if the result is in the results dictionary
        if task_id in self.results:
            return self.results[task_id]

        # Otherwise, check if the task has a result
        task = self.get_task(task_id)
        if task is not None and task.result is not None:
            return task.result

        return None

    def distribute_task(self, task_id: str, distributor_name: str = "capability_based_distributor") -> Optional[str]:
        """
        Distribute a task to an agent.

        Args:
            task_id: The ID of the task to distribute.
            distributor_name: The name of the task distributor to use.

        Returns:
            The ID of the agent assigned to the task, or None if the task couldn't be distributed.
        """
        # Get the task
        task = self.get_task(task_id)
        if task is None:
            return None

        # Get the distributor
        distributor = self.get_distributor(distributor_name)
        if distributor is None:
            return None

        # Distribute the task
        agent_id = distributor.distribute(task)

        return agent_id

    def send_task_message(
        self,
        task_id: str,
        agent_id: str,
        channel_name: str = "direct_channel",
        message_type: MessageType = MessageType.REQUEST,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send a task message to an agent.

        Args:
            task_id: The ID of the task.
            agent_id: The ID of the agent to send the message to.
            channel_name: The name of the communication channel to use.
            message_type: The type of message to send.
            priority: The priority of the message.
            metadata: Additional metadata for the message.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        # Get the task
        task = self.get_task(task_id)
        if task is None:
            return False

        # Get the channel
        channel = self.get_channel(channel_name)
        if channel is None:
            return False

        # Create the message
        message = AgentMessage(
            sender_id=self.name,
            recipient_id=agent_id,
            content=task,
            message_type=message_type,
            priority=priority,
            metadata=metadata or {}
        )

        # Send the message
        return channel.send_message(message)

    def receive_task_result(
        self,
        channel_name: str = "direct_channel",
        timeout: Optional[float] = None
    ) -> Optional[Tuple[str, TaskResult]]:
        """
        Receive a task result from an agent.

        Args:
            channel_name: The name of the communication channel to use.
            timeout: The maximum time to wait for a result, or None to wait indefinitely.

        Returns:
            Tuple of (task_id, result), or None if no result was received.
        """
        # Get the channel
        channel = self.get_channel(channel_name)
        if channel is None:
            return None

        # Receive a message
        message = channel.receive_message(self.name, timeout)
        if message is None:
            return None

        # Extract the task result
        if not isinstance(message.content, TaskResult):
            return None

        result = message.content

        # Store the result
        self.results[result.task_id] = result

        # Update the task
        task = self.get_task(result.task_id)
        if task is not None:
            task.complete(result)

        return (result.task_id, result)

    def aggregate_results(
        self,
        results: List[TaskResult],
        aggregator_name: str = "simple_aggregator"
    ) -> TaskResult:
        """
        Aggregate multiple task results into a single result.

        Args:
            results: The task results to aggregate.
            aggregator_name: The name of the result aggregator to use.

        Returns:
            The aggregated result.
        """
        # Get the aggregator
        aggregator = self.get_aggregator(aggregator_name)
        if aggregator is None:
            # If the aggregator doesn't exist, use a simple aggregator
            aggregator = SimpleAggregator()

        # Aggregate the results
        return aggregator.aggregate(results)

    def coordinate_task(
        self,
        task_id: str,
        pattern_name: str = "hierarchical_pattern",
        channel_name: str = "direct_channel",
        agent_ids: Optional[List[str]] = None
    ) -> Optional[TaskResult]:
        """
        Coordinate agents to accomplish a task.

        Args:
            task_id: The ID of the task to coordinate.
            pattern_name: The name of the coordination pattern to use.
            channel_name: The name of the communication channel to use.
            agent_ids: List of agent IDs to coordinate, or None to use all active agents.

        Returns:
            The result of the task, or None if the task couldn't be coordinated.
        """
        # Get the task
        task = self.get_task(task_id)
        if task is None:
            return None

        # Get the pattern
        pattern = self.get_pattern(pattern_name)
        if pattern is None:
            return None

        # Get the channel
        channel = self.get_channel(channel_name)
        if channel is None:
            return None

        # Get the agents
        if agent_ids is not None:
            agents = [self.registry.get_agent(agent_id) for agent_id in agent_ids]
            agents = [agent for agent in agents if agent is not None and agent.is_active]
        else:
            agents = self.registry.get_active_agents()

        # If there are no agents, return a failed result
        if not agents:
            return TaskResult(
                task_id=task_id,
                agent_id="",
                status=TaskStatus.FAILED,
                error="No agents available for coordination"
            )

        # Coordinate the agents
        result = pattern.coordinate(task, agents, channel)

        # Store the result
        self.results[task_id] = result

        # Update the task
        task.complete(result)

        return result

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the coordinator.

        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the coordinator.

        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.

        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.

        Args:
            agent_id: The ID of the agent.

        Returns:
            The agent, or None if it doesn't exist.
        """
        return self.registry.get_agent(agent_id)

    def get_all_agents(self) -> Dict[str, Agent]:
        """
        Get all registered agents.

        Returns:
            Dictionary of agents, keyed by ID.
        """
        return self.registry.get_all_agents()

    def send_message(
        self,
        from_agent_id: str,
        to_agent_id: str,
        message: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a message from one agent to another.

        Args:
            from_agent_id: ID of the sending agent.
            to_agent_id: ID of the receiving agent.
            message: Message content.
            metadata: Additional metadata for the message.

        Returns:
            Message information.
        """
        # This is a placeholder implementation
        message_id = str(uuid.uuid4())
        return {
            "id": message_id,
            "from_agent_id": from_agent_id,
            "to_agent_id": to_agent_id,
            "message": message,
            "metadata": metadata or {},
            "timestamp": time.time()
        }

    def process_message(
        self,
        message: Dict[str, Any],
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a message.

        Args:
            message: Message to process.
            agent_id: ID of the agent to process the message, or None to use the coordinator.

        Returns:
            Response message.
        """
        # This is a placeholder implementation
        return {
            "id": str(uuid.uuid4()),
            "in_reply_to": message.get("id"),
            "message": "Response to message",
            "timestamp": time.time()
        }

    async def process_message_async(
        self,
        message: Dict[str, Any],
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a message asynchronously.

        Args:
            message: Message to process.
            agent_id: ID of the agent to process the message, or None to use the coordinator.

        Returns:
            Response message.
        """
        # This is a placeholder implementation
        return {
            "id": str(uuid.uuid4()),
            "in_reply_to": message.get("id"),
            "message": "Response to message",
            "timestamp": time.time()
        }

    def get_conversation(
        self,
        agent1_id: str,
        agent2_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get the conversation between two agents.

        Args:
            agent1_id: ID of the first agent.
            agent2_id: ID of the second agent.
            limit: Maximum number of messages to return.

        Returns:
            List of messages.
        """
        # This is a placeholder implementation
        return [
            {
                "id": "1",
                "from_agent_id": agent1_id,
                "to_agent_id": agent2_id,
                "message": "Message from agent1 to agent2",
                "timestamp": time.time() - 100
            },
            {
                "id": "2",
                "from_agent_id": agent2_id,
                "to_agent_id": agent1_id,
                "message": "Response from agent2 to agent1",
                "timestamp": time.time() - 50
            }
        ]

    def get_agent_messages(
        self,
        agent_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get messages involving an agent.

        Args:
            agent_id: ID of the agent.
            limit: Maximum number of messages to return.

        Returns:
            List of messages.
        """
        # This is a placeholder implementation
        return [
            {
                "id": "1",
                "from_agent_id": agent_id,
                "to_agent_id": "other_agent",
                "message": "Message from agent to other_agent",
                "timestamp": time.time() - 100
            },
            {
                "id": "2",
                "from_agent_id": "other_agent",
                "to_agent_id": agent_id,
                "message": "Response from other_agent to agent",
                "timestamp": time.time() - 50
            }
        ]


# Singleton instance
_agent_coordinator: Optional[AgentCoordinator] = None

def get_agent_coordinator() -> AgentCoordinator:
    """
    Get the singleton instance of the agent coordinator.

    Returns:
        The agent coordinator instance.
    """
    global _agent_coordinator
    if _agent_coordinator is None:
        _agent_coordinator = AgentCoordinator()
    return _agent_coordinator
