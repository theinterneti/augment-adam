"""
Mock implementation of the AgentCoordinator class for testing.

This module contains a mock implementation of the AgentCoordinator class that can be used
for testing without depending on the actual implementation.
"""

import uuid
from typing import Dict, List, Any, Optional, Set, Union, Callable

from tests.unit.ai_agent.coordination.mock_task import (
    Task, TaskStatus, TaskPriority, TaskResult, AgentCapability
)


class AgentRegistry:
    """Registry for tracking available agents and their capabilities."""
    
    def __init__(self):
        """Initialize the agent registry."""
        self.agents = {}
    
    def register_agent(self, agent):
        """Register an agent with the registry."""
        self.agents[agent.id] = agent
        return agent.id
    
    def unregister_agent(self, agent_id):
        """Unregister an agent from the registry."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False
    
    def get_agent(self, agent_id):
        """Get an agent by ID."""
        return self.agents.get(agent_id)
    
    def get_active_agents(self):
        """Get all active agents."""
        return [agent for agent in self.agents.values() if agent.is_active]
    
    def get_agents_by_capability(self, capability):
        """Get agents with a specific capability."""
        return [
            agent for agent in self.agents.values()
            if agent.is_active and agent.has_capability(capability)
        ]


class Agent:
    """Agent in the coordination system."""
    
    def __init__(self, id=None, name=""):
        """Initialize the agent."""
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.is_active = True
        self.load = 0.0
        self.capabilities = set()
    
    def has_capability(self, capability):
        """Check if the agent has a capability."""
        return capability in self.capabilities


class DirectCommunicationChannel:
    """Communication channel for direct agent-to-agent messaging."""
    
    def __init__(self, name="direct_channel"):
        """Initialize the direct communication channel."""
        self.name = name
        self.message_queues = {}
    
    def send_message(self, message):
        """Send a message through the channel."""
        if message.recipient_id not in self.message_queues:
            self.message_queues[message.recipient_id] = []
        
        self.message_queues[message.recipient_id].append(message)
        return True
    
    def receive_message(self, agent_id, timeout=None):
        """Receive a message from the channel."""
        if agent_id not in self.message_queues or not self.message_queues[agent_id]:
            return None
        
        return self.message_queues[agent_id].pop(0)


class BroadcastCommunicationChannel:
    """Communication channel for broadcasting messages to all agents."""
    
    def __init__(self, name="broadcast_channel", registry=None):
        """Initialize the broadcast communication channel."""
        self.name = name
        self.registry = registry
        self.message_queues = {}
    
    def send_message(self, message):
        """Send a message through the channel."""
        if message.recipient_id is not None:
            if message.recipient_id not in self.message_queues:
                self.message_queues[message.recipient_id] = []
            
            self.message_queues[message.recipient_id].append(message)
            return True
        
        # Broadcast to all agents
        for agent in self.registry.get_active_agents():
            if agent.id == message.sender_id:
                continue
            
            if agent.id not in self.message_queues:
                self.message_queues[agent.id] = []
            
            self.message_queues[agent.id].append(message)
        
        return True
    
    def receive_message(self, agent_id, timeout=None):
        """Receive a message from the channel."""
        if agent_id not in self.message_queues or not self.message_queues[agent_id]:
            return None
        
        return self.message_queues[agent_id].pop(0)


class TopicCommunicationChannel:
    """Communication channel for topic-based messaging."""
    
    def __init__(self, name="topic_channel"):
        """Initialize the topic communication channel."""
        self.name = name
        self.subscriptions = {}
        self.message_queues = {}
    
    def subscribe(self, agent_id, topic):
        """Subscribe an agent to a topic."""
        if agent_id not in self.subscriptions:
            self.subscriptions[agent_id] = set()
        
        self.subscriptions[agent_id].add(topic)
    
    def unsubscribe(self, agent_id, topic):
        """Unsubscribe an agent from a topic."""
        if agent_id in self.subscriptions and topic in self.subscriptions[agent_id]:
            self.subscriptions[agent_id].remove(topic)
    
    def unsubscribe_all(self, agent_id):
        """Unsubscribe an agent from all topics."""
        if agent_id in self.subscriptions:
            self.subscriptions[agent_id] = set()
    
    def publish(self, topic, message):
        """Publish a message to a topic."""
        subscribers = []
        for agent_id, topics in self.subscriptions.items():
            if topic in topics:
                subscribers.append(agent_id)
        
        if not subscribers:
            return False
        
        for agent_id in subscribers:
            if agent_id == message.sender_id:
                continue
            
            if agent_id not in self.message_queues:
                self.message_queues[agent_id] = []
            
            self.message_queues[agent_id].append(message)
        
        return True
    
    def send_message(self, message):
        """Send a message through the channel."""
        topic = message.metadata.get("topic")
        if topic is None:
            return False
        
        return self.publish(topic, message)
    
    def receive_message(self, agent_id, timeout=None):
        """Receive a message from the channel."""
        if agent_id not in self.message_queues or not self.message_queues[agent_id]:
            return None
        
        return self.message_queues[agent_id].pop(0)


class RoundRobinDistributor:
    """Distributor that assigns tasks in a round-robin fashion."""
    
    def __init__(self, name="round_robin_distributor", registry=None):
        """Initialize the round-robin distributor."""
        self.name = name
        self.registry = registry
        self.last_agent_index = -1
    
    def distribute(self, task):
        """Distribute a task to an agent."""
        agents = self.registry.get_active_agents()
        if not agents:
            return None
        
        self.last_agent_index = (self.last_agent_index + 1) % len(agents)
        agent = agents[self.last_agent_index]
        
        task.assign(agent.id)
        return agent.id


class CapabilityBasedDistributor:
    """Distributor that assigns tasks based on agent capabilities."""
    
    def __init__(self, name="capability_based_distributor", registry=None):
        """Initialize the capability-based distributor."""
        self.name = name
        self.registry = registry
    
    def distribute(self, task):
        """Distribute a task to an agent."""
        if not task.required_capabilities:
            # If no capabilities are required, use any active agent
            agents = self.registry.get_active_agents()
            if not agents:
                return None
            
            agent = agents[0]
            task.assign(agent.id)
            return agent.id
        
        # Find agents with all required capabilities
        capable_agents = []
        for agent in self.registry.get_active_agents():
            has_all_capabilities = True
            for capability in task.required_capabilities:
                if not agent.has_capability(capability):
                    has_all_capabilities = False
                    break
            
            if has_all_capabilities:
                capable_agents.append(agent)
        
        if not capable_agents:
            return None
        
        # Choose the first capable agent
        agent = capable_agents[0]
        task.assign(agent.id)
        return agent.id


class LoadBalancedDistributor:
    """Distributor that assigns tasks based on agent load."""
    
    def __init__(self, name="load_balanced_distributor", registry=None):
        """Initialize the load-balanced distributor."""
        self.name = name
        self.registry = registry
    
    def distribute(self, task):
        """Distribute a task to an agent."""
        agents = self.registry.get_active_agents()
        if not agents:
            return None
        
        # Filter agents by capabilities if required
        if task.required_capabilities:
            capable_agents = []
            for agent in agents:
                has_all_capabilities = True
                for capability in task.required_capabilities:
                    if not agent.has_capability(capability):
                        has_all_capabilities = False
                        break
                
                if has_all_capabilities:
                    capable_agents.append(agent)
            
            agents = capable_agents
        
        if not agents:
            return None
        
        # Find the agent with the lowest load
        min_load_agent = min(agents, key=lambda a: a.load)
        
        task.assign(min_load_agent.id)
        return min_load_agent.id


class SimpleAggregator:
    """Aggregator that combines results using a simple strategy."""
    
    def __init__(self, name="simple_aggregator", strategy="first_success"):
        """Initialize the simple aggregator."""
        self.name = name
        self.strategy = strategy
    
    def aggregate(self, results):
        """Aggregate results."""
        if not results:
            return TaskResult(
                task_id="unknown",
                status=TaskStatus.FAILED,
                error="No results to aggregate"
            )
        
        # Filter out failed results
        successful_results = [r for r in results if r.is_successful()]
        
        if not successful_results:
            # If all results failed, return the first failure
            return results[0]
        
        if self.strategy == "first_success":
            # Return the first successful result
            return successful_results[0]
        
        elif self.strategy == "last_success":
            # Return the last successful result
            return successful_results[-1]
        
        elif self.strategy == "concatenate":
            # Concatenate all successful results
            combined_output = []
            for result in successful_results:
                if isinstance(result.output, list):
                    combined_output.extend(result.output)
                else:
                    combined_output.append(result.output)
            
            return TaskResult(
                task_id=successful_results[0].task_id,
                agent_id="aggregated",
                output=combined_output,
                status=TaskStatus.COMPLETED,
                metadata={"aggregated_from": [r.agent_id for r in successful_results]}
            )
        
        # Default to first successful result
        return successful_results[0]


class WeightedAggregator:
    """Aggregator that combines results using weighted averaging."""
    
    def __init__(self, name="weighted_aggregator", weights=None):
        """Initialize the weighted aggregator."""
        self.name = name
        self.weights = weights or {}
    
    def aggregate(self, results):
        """Aggregate results."""
        if not results:
            return TaskResult(
                task_id="unknown",
                status=TaskStatus.FAILED,
                error="No results to aggregate"
            )
        
        # Filter out failed results
        successful_results = [r for r in results if r.is_successful()]
        
        if not successful_results:
            # If all results failed, return the first failure
            return results[0]
        
        if len(successful_results) == 1:
            # If only one successful result, return it
            return successful_results[0]
        
        # Get weights for each result
        result_weights = {}
        for result in successful_results:
            agent_id = result.agent_id
            result_weights[agent_id] = self.weights.get(agent_id, 1.0)
        
        # Normalize weights
        total_weight = sum(result_weights.values())
        if total_weight == 0:
            # If all weights are zero, use equal weights
            for agent_id in result_weights:
                result_weights[agent_id] = 1.0 / len(result_weights)
        else:
            # Normalize weights
            for agent_id in result_weights:
                result_weights[agent_id] /= total_weight
        
        # Check if all outputs are numeric
        all_numeric = all(
            isinstance(r.output, (int, float))
            for r in successful_results
        )
        
        if all_numeric:
            # Compute weighted average
            weighted_output = sum(
                r.output * result_weights[r.agent_id]
                for r in successful_results
            )
            
            return TaskResult(
                task_id=successful_results[0].task_id,
                agent_id="aggregated",
                output=weighted_output,
                status=TaskStatus.COMPLETED,
                metadata={
                    "aggregated_from": [r.agent_id for r in successful_results],
                    "weights": result_weights
                }
            )
        
        # For non-numeric outputs, combine with weights
        if all(isinstance(r.output, list) for r in successful_results):
            # For lists, create a list of items with weights
            combined_output = []
            for result in successful_results:
                weight = result_weights[result.agent_id]
                for item in result.output:
                    combined_output.append({
                        "item": item,
                        "weight": weight,
                        "agent_id": result.agent_id
                    })
            
            return TaskResult(
                task_id=successful_results[0].task_id,
                agent_id="aggregated",
                output=combined_output,
                status=TaskStatus.COMPLETED,
                metadata={
                    "aggregated_from": [r.agent_id for r in successful_results],
                    "weights": result_weights
                }
            )
        
        # For string outputs, concatenate with weights
        combined_output = ""
        for result in successful_results:
            weight = result_weights[result.agent_id]
            combined_output += f"[Weight: {weight:.2f}] {result.output}\n\n"
        
        return TaskResult(
            task_id=successful_results[0].task_id,
            agent_id="aggregated",
            output=combined_output.strip(),
            status=TaskStatus.COMPLETED,
            metadata={
                "aggregated_from": [r.agent_id for r in successful_results],
                "weights": result_weights
            }
        )


class VotingAggregator:
    """Aggregator that combines results using voting."""
    
    def __init__(self, name="voting_aggregator", voting_method="majority"):
        """Initialize the voting aggregator."""
        self.name = name
        self.voting_method = voting_method
    
    def aggregate(self, results):
        """Aggregate results."""
        if not results:
            return TaskResult(
                task_id="unknown",
                status=TaskStatus.FAILED,
                error="No results to aggregate"
            )
        
        # Filter out failed results
        successful_results = [r for r in results if r.is_successful()]
        
        if not successful_results:
            # If all results failed, return the first failure
            return results[0]
        
        if len(successful_results) == 1:
            # If only one successful result, return it
            return successful_results[0]
        
        # Count votes for each output
        votes = {}
        for result in successful_results:
            output_str = str(result.output)
            if output_str not in votes:
                votes[output_str] = []
            votes[output_str].append(result)
        
        # Sort outputs by vote count
        sorted_outputs = sorted(
            votes.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        # Get the output with the most votes
        top_output, top_votes = sorted_outputs[0]
        total_votes = len(successful_results)
        
        # Check if we have a majority
        if self.voting_method == "majority" and len(top_votes) > total_votes / 2:
            # We have a majority
            return TaskResult(
                task_id=successful_results[0].task_id,
                agent_id="aggregated",
                output=top_votes[0].output,
                status=TaskStatus.COMPLETED,
                metadata={
                    "aggregated_from": [r.agent_id for r in top_votes],
                    "vote_count": len(top_votes),
                    "total_votes": total_votes,
                    "voting_method": "majority"
                }
            )
        
        # No majority, use plurality
        return TaskResult(
            task_id=successful_results[0].task_id,
            agent_id="aggregated",
            output=top_votes[0].output,
            status=TaskStatus.COMPLETED,
            metadata={
                "aggregated_from": [r.agent_id for r in top_votes],
                "vote_count": len(top_votes),
                "total_votes": total_votes,
                "voting_method": "plurality"
            }
        )


class AgentCoordinator:
    """Coordinator for managing agent coordination."""
    
    def __init__(self, name="agent_coordinator", registry=None):
        """Initialize the agent coordinator."""
        self.name = name
        self.registry = registry or AgentRegistry()
        self.tasks = {}
        self.channels = {}
        self.distributors = {}
        self.aggregators = {}
        self.patterns = {}
        
        # Register default components
        self.channels["direct_channel"] = DirectCommunicationChannel()
        self.channels["broadcast_channel"] = BroadcastCommunicationChannel(registry=self.registry)
        self.channels["topic_channel"] = TopicCommunicationChannel()
        
        self.distributors["round_robin_distributor"] = RoundRobinDistributor(registry=self.registry)
        self.distributors["capability_based_distributor"] = CapabilityBasedDistributor(registry=self.registry)
        self.distributors["load_balanced_distributor"] = LoadBalancedDistributor(registry=self.registry)
        
        self.aggregators["simple_aggregator"] = SimpleAggregator()
        self.aggregators["weighted_aggregator"] = WeightedAggregator()
        self.aggregators["voting_aggregator"] = VotingAggregator()
    
    def register_channel(self, channel):
        """Register a communication channel."""
        self.channels[channel.name] = channel
    
    def get_channel(self, name):
        """Get a communication channel by name."""
        return self.channels.get(name)
    
    def register_distributor(self, distributor):
        """Register a task distributor."""
        self.distributors[distributor.name] = distributor
    
    def get_distributor(self, name):
        """Get a task distributor by name."""
        return self.distributors.get(name)
    
    def register_aggregator(self, aggregator):
        """Register a result aggregator."""
        self.aggregators[aggregator.name] = aggregator
    
    def get_aggregator(self, name):
        """Get a result aggregator by name."""
        return self.aggregators.get(name)
    
    def register_pattern(self, pattern):
        """Register a coordination pattern."""
        self.patterns[pattern.name] = pattern
    
    def get_pattern(self, name):
        """Get a coordination pattern by name."""
        return self.patterns.get(name)
    
    def create_task(self, name, description="", input=None, required_capabilities=None,
                   priority=TaskPriority.NORMAL, metadata=None, tags=None):
        """Create a new task."""
        task = Task(
            name=name,
            description=description,
            input=input,
            required_capabilities=set(required_capabilities) if required_capabilities else set(),
            priority=priority,
            metadata=metadata,
            tags=tags
        )
        
        self.tasks[task.id] = task
        return task.id
    
    def add_task(self, task):
        """Add an existing task."""
        self.tasks[task.id] = task
        return task.id
    
    def get_task(self, task_id):
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def create_subtask(self, parent_task_id, name, description="", input=None,
                      required_capabilities=None, priority=TaskPriority.NORMAL,
                      metadata=None, tags=None):
        """Create a subtask of a parent task."""
        parent_task = self.get_task(parent_task_id)
        if parent_task is None:
            return None
        
        subtask = Task(
            name=name,
            description=description,
            input=input,
            required_capabilities=set(required_capabilities) if required_capabilities else set(),
            priority=priority,
            parent_task_id=parent_task_id,
            metadata=metadata,
            tags=tags
        )
        
        self.tasks[subtask.id] = subtask
        parent_task.subtask_ids.append(subtask.id)
        
        return subtask.id
    
    def distribute_task(self, task_id, distributor_name):
        """Distribute a task to an agent."""
        task = self.get_task(task_id)
        if task is None:
            return None
        
        distributor = self.get_distributor(distributor_name)
        if distributor is None:
            return None
        
        return distributor.distribute(task)
    
    def update_task_result(self, task_id, result):
        """Update a task with a result."""
        task = self.get_task(task_id)
        if task is None:
            return False
        
        task.complete(result)
        return True
    
    def aggregate_results(self, results, aggregator_name):
        """Aggregate results."""
        aggregator = self.get_aggregator(aggregator_name)
        if aggregator is None:
            # Use a default aggregator
            aggregator = SimpleAggregator()
        
        return aggregator.aggregate(results)
    
    def coordinate_task(self, task_id, pattern_name, channel_name, agent_ids=None):
        """Coordinate a task using a pattern."""
        task = self.get_task(task_id)
        if task is None:
            return None
        
        pattern = self.get_pattern(pattern_name)
        if pattern is None:
            return None
        
        channel = self.get_channel(channel_name)
        if channel is None:
            return None
        
        agents = []
        if agent_ids:
            for agent_id in agent_ids:
                agent = self.registry.get_agent(agent_id)
                if agent:
                    agents.append(agent)
        else:
            agents = self.registry.get_active_agents()
        
        result = pattern.coordinate(task, agents, channel)
        
        if result:
            task.complete(result)
        
        return result


_agent_coordinator_instance = None

def get_agent_coordinator():
    """Get the singleton instance of the agent coordinator."""
    global _agent_coordinator_instance
    if _agent_coordinator_instance is None:
        _agent_coordinator_instance = AgentCoordinator()
    
    return _agent_coordinator_instance
