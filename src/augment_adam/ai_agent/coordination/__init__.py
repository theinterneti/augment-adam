"""
Agent Coordination System.

This module provides a system for coordinating multiple agents to work together
on complex tasks, including agent registry, communication, task distribution,
and result aggregation.

TODO(Issue #8): Add support for agent coordination analytics
TODO(Issue #8): Implement more coordination patterns
TODO(Issue #8): Add support for dynamic agent discovery
"""

from augment_adam.ai_agent.coordination.registry import (
    AgentRegistry,
    AgentCapability,
    get_agent_registry,
)

from augment_adam.ai_agent.coordination.communication import (
    AgentMessage,
    MessageType,
    MessagePriority,
    AgentCommunicationChannel,
    DirectCommunicationChannel,
    BroadcastCommunicationChannel,
    TopicCommunicationChannel,
)

from augment_adam.ai_agent.coordination.task import (
    Task,
    TaskStatus,
    TaskPriority,
    TaskResult,
    TaskDistributor,
    RoundRobinDistributor,
    CapabilityBasedDistributor,
    LoadBalancedDistributor,
)

from augment_adam.ai_agent.coordination.aggregation import (
    ResultAggregator,
    SimpleAggregator,
    WeightedAggregator,
    VotingAggregator,
)

from augment_adam.ai_agent.coordination.patterns import (
    CoordinationPattern,
    HierarchicalPattern,
    PeerToPeerPattern,
    MarketBasedPattern,
)

from augment_adam.ai_agent.coordination.coordinator import (
    AgentCoordinator,
    get_agent_coordinator,
)

from augment_adam.ai_agent.coordination.team import (
    AgentTeam,
)

from augment_adam.ai_agent.coordination.workflow import (
    Workflow,
    WorkflowStep,
)

__all__ = [
    # Registry
    "AgentRegistry",
    "AgentCapability",
    "get_agent_registry",

    # Communication
    "AgentMessage",
    "MessageType",
    "MessagePriority",
    "AgentCommunicationChannel",
    "DirectCommunicationChannel",
    "BroadcastCommunicationChannel",
    "TopicCommunicationChannel",

    # Task
    "Task",
    "TaskStatus",
    "TaskPriority",
    "TaskResult",
    "TaskDistributor",
    "RoundRobinDistributor",
    "CapabilityBasedDistributor",
    "LoadBalancedDistributor",

    # Aggregation
    "ResultAggregator",
    "SimpleAggregator",
    "WeightedAggregator",
    "VotingAggregator",

    # Patterns
    "CoordinationPattern",
    "HierarchicalPattern",
    "PeerToPeerPattern",
    "MarketBasedPattern",

    # Coordinator
    "AgentCoordinator",
    "get_agent_coordinator",

    # Team
    "AgentTeam",

    # Workflow
    "Workflow",
    "WorkflowStep",
]