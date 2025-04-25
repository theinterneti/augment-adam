"""
Coordination Patterns module.

This module provides patterns for coordinating multiple agents, including
hierarchical, peer-to-peer, and market-based patterns.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.ai_agent.coordination.registry import Agent, AgentRegistry, get_agent_registry
from augment_adam.ai_agent.coordination.communication import (
    AgentMessage, MessageType, MessagePriority, AgentCommunicationChannel
)
from augment_adam.ai_agent.coordination.task import Task, TaskResult, TaskStatus, TaskDistributor


@tag("ai_agent.coordination")
class CoordinationPattern(ABC):
    """
    Base class for coordination patterns.
    
    This class defines the interface for coordination patterns, which
    determine how agents work together to accomplish tasks.
    
    Attributes:
        name: The name of the coordination pattern.
        registry: The agent registry to use for coordination.
        metadata: Additional metadata for the pattern.
    
    TODO(Issue #8): Add support for pattern validation
    TODO(Issue #8): Implement pattern analytics
    """
    
    def __init__(self, name: str, registry: Optional[AgentRegistry] = None) -> None:
        """
        Initialize the coordination pattern.
        
        Args:
            name: The name of the coordination pattern.
            registry: The agent registry to use for coordination.
        """
        self.name = name
        self.registry = registry or get_agent_registry()
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def coordinate(self, task: Task, agents: List[Agent], channel: AgentCommunicationChannel) -> TaskResult:
        """
        Coordinate agents to accomplish a task.
        
        Args:
            task: The task to accomplish.
            agents: The agents to coordinate.
            channel: The communication channel to use.
            
        Returns:
            The result of the task.
        """
        pass
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the pattern.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the pattern.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("ai_agent.coordination")
class HierarchicalPattern(CoordinationPattern):
    """
    Hierarchical coordination pattern.
    
    This class implements a hierarchical coordination pattern, where a
    manager agent delegates subtasks to worker agents and aggregates their results.
    
    Attributes:
        name: The name of the coordination pattern.
        registry: The agent registry to use for coordination.
        metadata: Additional metadata for the pattern.
        manager_id: ID of the manager agent.
        distributor: The task distributor to use for subtask distribution.
    
    TODO(Issue #8): Add support for multiple levels of hierarchy
    TODO(Issue #8): Implement pattern validation
    """
    
    def __init__(
        self,
        name: str = "hierarchical_pattern",
        registry: Optional[AgentRegistry] = None,
        manager_id: Optional[str] = None,
        distributor: Optional[TaskDistributor] = None
    ) -> None:
        """
        Initialize the hierarchical coordination pattern.
        
        Args:
            name: The name of the coordination pattern.
            registry: The agent registry to use for coordination.
            manager_id: ID of the manager agent.
            distributor: The task distributor to use for subtask distribution.
        """
        super().__init__(name, registry)
        self.manager_id = manager_id
        self.distributor = distributor
        self.metadata["manager_id"] = manager_id
    
    def set_manager(self, manager_id: str) -> None:
        """
        Set the manager agent.
        
        Args:
            manager_id: ID of the manager agent.
        """
        self.manager_id = manager_id
        self.metadata["manager_id"] = manager_id
    
    def set_distributor(self, distributor: TaskDistributor) -> None:
        """
        Set the task distributor.
        
        Args:
            distributor: The task distributor to use for subtask distribution.
        """
        self.distributor = distributor
    
    def coordinate(self, task: Task, agents: List[Agent], channel: AgentCommunicationChannel) -> TaskResult:
        """
        Coordinate agents in a hierarchical pattern.
        
        Args:
            task: The task to accomplish.
            agents: The agents to coordinate.
            channel: The communication channel to use.
            
        Returns:
            The result of the task.
        """
        # If there are no agents, return a failed result
        if not agents:
            return TaskResult(
                task_id=task.id,
                agent_id="",
                status=TaskStatus.FAILED,
                error="No agents available for coordination"
            )
        
        # If there's only one agent, assign the task directly
        if len(agents) == 1:
            agent = agents[0]
            task.assign(agent.id)
            
            # Create a message for the agent
            message = AgentMessage(
                sender_id="coordinator",
                recipient_id=agent.id,
                content=task,
                message_type=MessageType.REQUEST
            )
            
            # Send the message
            channel.send_message(message)
            
            # Wait for a response
            response = channel.receive_message("coordinator")
            
            # If there's no response, return a failed result
            if response is None:
                return TaskResult(
                    task_id=task.id,
                    agent_id=agent.id,
                    status=TaskStatus.FAILED,
                    error="No response from agent"
                )
            
            # Return the result
            return response.content
        
        # Select a manager agent
        manager = None
        if self.manager_id is not None:
            # Use the specified manager
            for agent in agents:
                if agent.id == self.manager_id:
                    manager = agent
                    break
        
        # If no manager was found, select the first agent
        if manager is None:
            manager = agents[0]
        
        # Create worker agents (all agents except the manager)
        workers = [agent for agent in agents if agent.id != manager.id]
        
        # Create a message for the manager
        manager_message = AgentMessage(
            sender_id="coordinator",
            recipient_id=manager.id,
            content={
                "task": task,
                "workers": [worker.id for worker in workers]
            },
            message_type=MessageType.REQUEST
        )
        
        # Send the message to the manager
        channel.send_message(manager_message)
        
        # Wait for the manager to create subtasks
        subtasks_message = channel.receive_message("coordinator")
        
        # If there's no response, return a failed result
        if subtasks_message is None:
            return TaskResult(
                task_id=task.id,
                agent_id=manager.id,
                status=TaskStatus.FAILED,
                error="No response from manager"
            )
        
        # Get the subtasks
        subtasks = subtasks_message.content.get("subtasks", [])
        
        # If there are no subtasks, return a failed result
        if not subtasks:
            return TaskResult(
                task_id=task.id,
                agent_id=manager.id,
                status=TaskStatus.FAILED,
                error="Manager did not create any subtasks"
            )
        
        # Distribute subtasks to workers
        for subtask in subtasks:
            # If a distributor is provided, use it
            if self.distributor is not None:
                worker_id = self.distributor.distribute(subtask)
            else:
                # Otherwise, assign to the first available worker
                worker_id = workers[0].id if workers else None
            
            # If no worker was assigned, skip this subtask
            if worker_id is None:
                continue
            
            # Create a message for the worker
            worker_message = AgentMessage(
                sender_id="coordinator",
                recipient_id=worker_id,
                content=subtask,
                message_type=MessageType.REQUEST
            )
            
            # Send the message to the worker
            channel.send_message(worker_message)
        
        # Collect results from workers
        results = []
        for _ in range(len(subtasks)):
            # Wait for a response
            response = channel.receive_message("coordinator", timeout=10.0)
            
            # If there's no response, continue
            if response is None:
                continue
            
            # Add the result
            results.append(response.content)
        
        # Send results to the manager for aggregation
        aggregation_message = AgentMessage(
            sender_id="coordinator",
            recipient_id=manager.id,
            content={
                "task": task,
                "results": results
            },
            message_type=MessageType.REQUEST
        )
        
        # Send the message to the manager
        channel.send_message(aggregation_message)
        
        # Wait for the manager to aggregate results
        final_result_message = channel.receive_message("coordinator")
        
        # If there's no response, return a failed result
        if final_result_message is None:
            return TaskResult(
                task_id=task.id,
                agent_id=manager.id,
                status=TaskStatus.FAILED,
                error="No final result from manager"
            )
        
        # Return the final result
        return final_result_message.content


@tag("ai_agent.coordination")
class PeerToPeerPattern(CoordinationPattern):
    """
    Peer-to-peer coordination pattern.
    
    This class implements a peer-to-peer coordination pattern, where agents
    collaborate as equals to accomplish a task.
    
    Attributes:
        name: The name of the coordination pattern.
        registry: The agent registry to use for coordination.
        metadata: Additional metadata for the pattern.
        max_rounds: Maximum number of coordination rounds.
    
    TODO(Issue #8): Add support for more sophisticated peer-to-peer protocols
    TODO(Issue #8): Implement pattern validation
    """
    
    def __init__(
        self,
        name: str = "peer_to_peer_pattern",
        registry: Optional[AgentRegistry] = None,
        max_rounds: int = 5
    ) -> None:
        """
        Initialize the peer-to-peer coordination pattern.
        
        Args:
            name: The name of the coordination pattern.
            registry: The agent registry to use for coordination.
            max_rounds: Maximum number of coordination rounds.
        """
        super().__init__(name, registry)
        self.max_rounds = max_rounds
        self.metadata["max_rounds"] = max_rounds
    
    def coordinate(self, task: Task, agents: List[Agent], channel: AgentCommunicationChannel) -> TaskResult:
        """
        Coordinate agents in a peer-to-peer pattern.
        
        Args:
            task: The task to accomplish.
            agents: The agents to coordinate.
            channel: The communication channel to use.
            
        Returns:
            The result of the task.
        """
        # If there are no agents, return a failed result
        if not agents:
            return TaskResult(
                task_id=task.id,
                agent_id="",
                status=TaskStatus.FAILED,
                error="No agents available for coordination"
            )
        
        # If there's only one agent, assign the task directly
        if len(agents) == 1:
            agent = agents[0]
            task.assign(agent.id)
            
            # Create a message for the agent
            message = AgentMessage(
                sender_id="coordinator",
                recipient_id=agent.id,
                content=task,
                message_type=MessageType.REQUEST
            )
            
            # Send the message
            channel.send_message(message)
            
            # Wait for a response
            response = channel.receive_message("coordinator")
            
            # If there's no response, return a failed result
            if response is None:
                return TaskResult(
                    task_id=task.id,
                    agent_id=agent.id,
                    status=TaskStatus.FAILED,
                    error="No response from agent"
                )
            
            # Return the result
            return response.content
        
        # Initialize agent states
        agent_states = {agent.id: {"status": "ready", "result": None} for agent in agents}
        
        # Create initial messages for all agents
        for agent in agents:
            # Create a message for the agent
            message = AgentMessage(
                sender_id="coordinator",
                recipient_id=agent.id,
                content={
                    "task": task,
                    "peers": [a.id for a in agents if a.id != agent.id],
                    "round": 0
                },
                message_type=MessageType.REQUEST
            )
            
            # Send the message
            channel.send_message(message)
        
        # Coordinate for multiple rounds
        final_results = []
        for round_num in range(1, self.max_rounds + 1):
            # Collect responses from all agents
            responses = []
            for _ in range(len(agents)):
                # Wait for a response
                response = channel.receive_message("coordinator", timeout=10.0)
                
                # If there's no response, continue
                if response is None:
                    continue
                
                # Add the response
                responses.append(response)
            
            # Process responses
            for response in responses:
                agent_id = response.sender_id
                content = response.content
                
                # Update agent state
                if "status" in content:
                    agent_states[agent_id]["status"] = content["status"]
                
                if "result" in content:
                    agent_states[agent_id]["result"] = content["result"]
                    final_results.append(content["result"])
                
                # If the agent is done, skip sending a new message
                if agent_states[agent_id]["status"] in ["done", "failed"]:
                    continue
                
                # Create a message for the next round
                message = AgentMessage(
                    sender_id="coordinator",
                    recipient_id=agent_id,
                    content={
                        "task": task,
                        "peers": [a.id for a in agents if a.id != agent_id],
                        "round": round_num,
                        "peer_states": {
                            peer_id: state for peer_id, state in agent_states.items() if peer_id != agent_id
                        }
                    },
                    message_type=MessageType.REQUEST
                )
                
                # Send the message
                channel.send_message(message)
            
            # Check if all agents are done
            if all(state["status"] in ["done", "failed"] for state in agent_states.values()):
                break
        
        # If there are no results, return a failed result
        if not final_results:
            return TaskResult(
                task_id=task.id,
                agent_id="coordinator",
                status=TaskStatus.FAILED,
                error="No results from agents"
            )
        
        # Return the first successful result
        for result in final_results:
            if result.status == TaskStatus.COMPLETED:
                return result
        
        # If there are no successful results, return the first result
        return final_results[0]


@tag("ai_agent.coordination")
class MarketBasedPattern(CoordinationPattern):
    """
    Market-based coordination pattern.
    
    This class implements a market-based coordination pattern, where agents
    bid on tasks and the highest bidder is assigned the task.
    
    Attributes:
        name: The name of the coordination pattern.
        registry: The agent registry to use for coordination.
        metadata: Additional metadata for the pattern.
        bid_timeout: Timeout for collecting bids.
    
    TODO(Issue #8): Add support for more sophisticated market mechanisms
    TODO(Issue #8): Implement pattern validation
    """
    
    def __init__(
        self,
        name: str = "market_based_pattern",
        registry: Optional[AgentRegistry] = None,
        bid_timeout: float = 5.0
    ) -> None:
        """
        Initialize the market-based coordination pattern.
        
        Args:
            name: The name of the coordination pattern.
            registry: The agent registry to use for coordination.
            bid_timeout: Timeout for collecting bids.
        """
        super().__init__(name, registry)
        self.bid_timeout = bid_timeout
        self.metadata["bid_timeout"] = bid_timeout
    
    def coordinate(self, task: Task, agents: List[Agent], channel: AgentCommunicationChannel) -> TaskResult:
        """
        Coordinate agents in a market-based pattern.
        
        Args:
            task: The task to accomplish.
            agents: The agents to coordinate.
            channel: The communication channel to use.
            
        Returns:
            The result of the task.
        """
        # If there are no agents, return a failed result
        if not agents:
            return TaskResult(
                task_id=task.id,
                agent_id="",
                status=TaskStatus.FAILED,
                error="No agents available for coordination"
            )
        
        # If there's only one agent, assign the task directly
        if len(agents) == 1:
            agent = agents[0]
            task.assign(agent.id)
            
            # Create a message for the agent
            message = AgentMessage(
                sender_id="coordinator",
                recipient_id=agent.id,
                content=task,
                message_type=MessageType.REQUEST
            )
            
            # Send the message
            channel.send_message(message)
            
            # Wait for a response
            response = channel.receive_message("coordinator")
            
            # If there's no response, return a failed result
            if response is None:
                return TaskResult(
                    task_id=task.id,
                    agent_id=agent.id,
                    status=TaskStatus.FAILED,
                    error="No response from agent"
                )
            
            # Return the result
            return response.content
        
        # Create bid request messages for all agents
        for agent in agents:
            # Create a message for the agent
            message = AgentMessage(
                sender_id="coordinator",
                recipient_id=agent.id,
                content={
                    "task": task,
                    "action": "bid"
                },
                message_type=MessageType.REQUEST
            )
            
            # Send the message
            channel.send_message(message)
        
        # Collect bids from agents
        bids = []
        start_time = time.time()
        while time.time() - start_time < self.bid_timeout and len(bids) < len(agents):
            # Wait for a response
            response = channel.receive_message("coordinator", timeout=0.1)
            
            # If there's no response, continue
            if response is None:
                continue
            
            # Add the bid
            bids.append(response)
        
        # If there are no bids, return a failed result
        if not bids:
            return TaskResult(
                task_id=task.id,
                agent_id="coordinator",
                status=TaskStatus.FAILED,
                error="No bids from agents"
            )
        
        # Select the highest bidder
        best_bid = max(bids, key=lambda bid: bid.content.get("bid", 0.0))
        best_agent_id = best_bid.sender_id
        
        # Assign the task to the highest bidder
        task.assign(best_agent_id)
        
        # Create a message for the winning agent
        message = AgentMessage(
            sender_id="coordinator",
            recipient_id=best_agent_id,
            content={
                "task": task,
                "action": "execute"
            },
            message_type=MessageType.REQUEST
        )
        
        # Send the message
        channel.send_message(message)
        
        # Notify other agents that they didn't win
        for agent in agents:
            if agent.id != best_agent_id:
                # Create a message for the agent
                message = AgentMessage(
                    sender_id="coordinator",
                    recipient_id=agent.id,
                    content={
                        "task_id": task.id,
                        "action": "reject"
                    },
                    message_type=MessageType.NOTIFICATION
                )
                
                # Send the message
                channel.send_message(message)
        
        # Wait for the result from the winning agent
        result_message = channel.receive_message("coordinator")
        
        # If there's no response, return a failed result
        if result_message is None:
            return TaskResult(
                task_id=task.id,
                agent_id=best_agent_id,
                status=TaskStatus.FAILED,
                error="No result from winning agent"
            )
        
        # Return the result
        return result_message.content
