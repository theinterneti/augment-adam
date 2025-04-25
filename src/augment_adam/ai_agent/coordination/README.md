# Agent Coordination System

## Overview

This module provides a system for coordinating multiple agents to work together on complex tasks, including agent registry, communication, task distribution, and result aggregation.

## Components

### Registry

The registry module provides a registry for tracking available agents and their capabilities:

- **AgentRegistry**: Registry for tracking available agents and their capabilities
- **Agent**: Agent in the coordination system
- **AgentCapability**: Capabilities that agents can have

### Communication

The communication module provides communication channels for agents to exchange messages:

- **AgentCommunicationChannel**: Base class for agent communication channels
- **DirectCommunicationChannel**: Communication channel for direct agent-to-agent messaging
- **BroadcastCommunicationChannel**: Communication channel for broadcasting messages to all agents
- **TopicCommunicationChannel**: Communication channel for topic-based messaging
- **AgentMessage**: Message exchanged between agents
- **MessageType**: Types of messages that agents can exchange
- **MessagePriority**: Priorities for agent messages

### Task

The task module provides classes for representing and distributing tasks among agents:

- **Task**: Task for agents to perform
- **TaskStatus**: Status of a task
- **TaskPriority**: Priority of a task
- **TaskResult**: Result of a completed task
- **TaskDistributor**: Base class for task distributors
- **RoundRobinDistributor**: Task distributor that assigns tasks in a round-robin fashion
- **CapabilityBasedDistributor**: Task distributor that assigns tasks based on agent capabilities
- **LoadBalancedDistributor**: Task distributor that assigns tasks based on agent load

### Aggregation

The aggregation module provides aggregators for combining results from multiple agents:

- **ResultAggregator**: Base class for result aggregators
- **SimpleAggregator**: Simple result aggregator that combines results using a specified strategy
- **WeightedAggregator**: Weighted result aggregator that combines results using weights
- **VotingAggregator**: Voting result aggregator that combines results using voting

### Patterns

The patterns module provides patterns for coordinating multiple agents:

- **CoordinationPattern**: Base class for coordination patterns
- **HierarchicalPattern**: Hierarchical coordination pattern
- **PeerToPeerPattern**: Peer-to-peer coordination pattern
- **MarketBasedPattern**: Market-based coordination pattern

### Coordinator

The coordinator module provides a coordinator for managing agent coordination:

- **AgentCoordinator**: Coordinator for managing agent coordination

## Usage

### Creating and Registering Agents

```python
from augment_adam.ai_agent.coordination import (
    Agent, AgentCapability, get_agent_registry
)

# Get the agent registry
registry = get_agent_registry()

# Create an agent
agent = Agent(
    name="text_generator",
    capabilities={
        AgentCapability.TEXT_GENERATION,
        AgentCapability.REASONING
    },
    metadata={"model": "gpt-4"}
)

# Register the agent
agent_id = registry.register_agent(agent)

# Get an agent by ID
agent = registry.get_agent(agent_id)

# Get agents by capability
text_generators = registry.get_agents_by_capability(AgentCapability.TEXT_GENERATION)
```

### Creating and Distributing Tasks

```python
from augment_adam.ai_agent.coordination import (
    Task, TaskPriority, CapabilityBasedDistributor
)

# Create a task
task = Task(
    name="Generate a story",
    description="Generate a short story about a robot learning to paint",
    input={"theme": "creativity", "length": "short"},
    required_capabilities={AgentCapability.TEXT_GENERATION},
    priority=TaskPriority.NORMAL
)

# Create a distributor
distributor = CapabilityBasedDistributor(registry=registry)

# Distribute the task
agent_id = distributor.distribute(task)

# Check if the task is assigned
if task.is_assigned():
    print(f"Task assigned to agent {task.assigned_agent_id}")
```

### Agent Communication

```python
from augment_adam.ai_agent.coordination import (
    AgentMessage, MessageType, MessagePriority,
    DirectCommunicationChannel
)

# Create a communication channel
channel = DirectCommunicationChannel()

# Create a message
message = AgentMessage(
    sender_id="agent1",
    recipient_id="agent2",
    content="Hello, Agent 2!",
    message_type=MessageType.NOTIFICATION,
    priority=MessagePriority.NORMAL
)

# Send the message
channel.send_message(message)

# Receive a message
received_message = channel.receive_message("agent2")
```

### Result Aggregation

```python
from augment_adam.ai_agent.coordination import (
    TaskResult, TaskStatus, WeightedAggregator
)

# Create task results
result1 = TaskResult(
    task_id="task1",
    agent_id="agent1",
    output="Result from Agent 1",
    status=TaskStatus.COMPLETED
)

result2 = TaskResult(
    task_id="task1",
    agent_id="agent2",
    output="Result from Agent 2",
    status=TaskStatus.COMPLETED
)

# Create an aggregator
aggregator = WeightedAggregator()
aggregator.set_weight("agent1", 0.7)
aggregator.set_weight("agent2", 0.3)

# Aggregate results
aggregated_result = aggregator.aggregate([result1, result2])
```

### Using Coordination Patterns

```python
from augment_adam.ai_agent.coordination import (
    HierarchicalPattern, DirectCommunicationChannel
)

# Create a coordination pattern
pattern = HierarchicalPattern(registry=registry)

# Get agents to coordinate
agents = registry.get_active_agents()

# Create a communication channel
channel = DirectCommunicationChannel()

# Coordinate agents to accomplish a task
result = pattern.coordinate(task, agents, channel)
```

### Using the Agent Coordinator

```python
from augment_adam.ai_agent.coordination import get_agent_coordinator

# Get the agent coordinator
coordinator = get_agent_coordinator()

# Create a task
task_id = coordinator.create_task(
    name="Generate a story",
    description="Generate a short story about a robot learning to paint",
    input={"theme": "creativity", "length": "short"},
    required_capabilities=[AgentCapability.TEXT_GENERATION],
    priority=TaskPriority.NORMAL
)

# Distribute the task
agent_id = coordinator.distribute_task(task_id, "capability_based_distributor")

# Send a task message to the agent
coordinator.send_task_message(task_id, agent_id)

# Receive a task result
task_id, result = coordinator.receive_task_result()

# Coordinate multiple agents to accomplish a task
result = coordinator.coordinate_task(
    task_id,
    pattern_name="hierarchical_pattern",
    channel_name="direct_channel"
)
```

## TODOs

- Add support for agent coordination analytics (Issue #8)
- Implement more coordination patterns (Issue #8)
- Add support for dynamic agent discovery (Issue #8)
- Add support for agent versioning (Issue #8)
- Implement agent validation (Issue #8)
- Add support for message encryption (Issue #8)
- Implement message validation (Issue #8)
- Add support for task versioning (Issue #8)
- Implement task validation (Issue #8)
- Add support for result validation (Issue #8)
- Add support for more aggregation strategies (Issue #8)
- Implement aggregator validation (Issue #8)
- Add support for more sophisticated peer-to-peer protocols (Issue #8)
- Implement pattern validation (Issue #8)
- Add support for coordinator persistence (Issue #8)
- Implement coordinator validation (Issue #8)
