"""Agent Coordinator Implementation.

This module provides the coordinator for managing multiple agents.

Version: 0.1.0
Created: 2025-05-01
"""

import logging
import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional, Union, Callable

from augment_adam.ai_agent.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Agent Coordinator.
    
    This class coordinates interactions between multiple agents.
    
    Attributes:
        name: Name of the coordinator
        agents: Dictionary mapping agent IDs to agent instances
        message_history: History of messages between agents
    """
    
    def __init__(
        self,
        name: str,
        agents: Optional[Dict[str, BaseAgent]] = None
    ):
        """Initialize the Agent Coordinator.
        
        Args:
            name: Name of the coordinator
            agents: Dictionary mapping agent IDs to agent instances
        """
        self.name = name
        self.agents = agents or {}
        self.message_history = []
        
        logger.info(f"Initialized Agent Coordinator '{name}' with {len(self.agents)} agents")
    
    def register_agent(self, agent_id: str, agent: BaseAgent) -> None:
        """Register an agent with the coordinator.
        
        Args:
            agent_id: ID for the agent
            agent: Agent instance
        """
        if agent_id in self.agents:
            logger.warning(f"Agent '{agent_id}' already registered, overwriting")
        
        self.agents[agent_id] = agent
        logger.info(f"Registered agent '{agent_id}' with coordinator '{self.name}'")
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the coordinator.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Returns:
            True if agent was unregistered, False otherwise
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Unregistered agent '{agent_id}' from coordinator '{self.name}'")
            return True
        else:
            logger.warning(f"Agent '{agent_id}' not found in coordinator '{self.name}'")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID.
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_id)
    
    def send_message(
        self,
        from_agent_id: str,
        to_agent_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a message from one agent to another.
        
        Args:
            from_agent_id: ID of the sending agent
            to_agent_id: ID of the receiving agent
            message: Message content
            metadata: Additional metadata
            
        Returns:
            Message object
            
        Raises:
            ValueError: If agent not found
        """
        # Check if agents exist
        if from_agent_id not in self.agents:
            raise ValueError(f"Agent '{from_agent_id}' not found")
        
        if to_agent_id not in self.agents:
            raise ValueError(f"Agent '{to_agent_id}' not found")
        
        # Create message
        message_obj = {
            "id": str(uuid.uuid4()),
            "from": from_agent_id,
            "to": to_agent_id,
            "message": message,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        
        # Add to history
        self.message_history.append(message_obj)
        
        logger.info(f"Sent message from '{from_agent_id}' to '{to_agent_id}'")
        return message_obj
    
    def process_message(
        self,
        message_obj: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a message by sending it to the receiving agent.
        
        Args:
            message_obj: Message object
            context: Additional context
            
        Returns:
            Response from the receiving agent
            
        Raises:
            ValueError: If agent not found
        """
        to_agent_id = message_obj["to"]
        
        # Check if agent exists
        if to_agent_id not in self.agents:
            raise ValueError(f"Agent '{to_agent_id}' not found")
        
        # Get agent
        agent = self.agents[to_agent_id]
        
        # Process message
        result = agent.process(message_obj["message"])
        
        # Create response
        response_obj = {
            "id": str(uuid.uuid4()),
            "from": to_agent_id,
            "to": message_obj["from"],
            "message": result["response"],
            "in_response_to": message_obj["id"],
            "metadata": {
                "original_metadata": message_obj.get("metadata", {}),
                "result_metadata": result.get("metadata", {})
            },
            "timestamp": time.time()
        }
        
        # Add to history
        self.message_history.append(response_obj)
        
        logger.info(f"Processed message from '{message_obj['from']}' to '{to_agent_id}'")
        return response_obj
    
    async def process_message_async(
        self,
        message_obj: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a message asynchronously.
        
        Args:
            message_obj: Message object
            context: Additional context
            
        Returns:
            Response from the receiving agent
            
        Raises:
            ValueError: If agent not found
        """
        to_agent_id = message_obj["to"]
        
        # Check if agent exists
        if to_agent_id not in self.agents:
            raise ValueError(f"Agent '{to_agent_id}' not found")
        
        # Get agent
        agent = self.agents[to_agent_id]
        
        # Process message
        if hasattr(agent, "process_async"):
            result = await agent.process_async(message_obj["message"])
        else:
            # Run synchronous process in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: agent.process(message_obj["message"])
            )
        
        # Create response
        response_obj = {
            "id": str(uuid.uuid4()),
            "from": to_agent_id,
            "to": message_obj["from"],
            "message": result["response"],
            "in_response_to": message_obj["id"],
            "metadata": {
                "original_metadata": message_obj.get("metadata", {}),
                "result_metadata": result.get("metadata", {})
            },
            "timestamp": time.time()
        }
        
        # Add to history
        self.message_history.append(response_obj)
        
        logger.info(f"Processed message asynchronously from '{message_obj['from']}' to '{to_agent_id}'")
        return response_obj
    
    def get_conversation(
        self,
        agent_id1: str,
        agent_id2: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation between two agents.
        
        Args:
            agent_id1: ID of the first agent
            agent_id2: ID of the second agent
            limit: Maximum number of messages to return
            
        Returns:
            List of messages between the agents
        """
        # Filter messages between the two agents
        conversation = [
            msg for msg in self.message_history
            if (msg["from"] == agent_id1 and msg["to"] == agent_id2) or
               (msg["from"] == agent_id2 and msg["to"] == agent_id1)
        ]
        
        # Sort by timestamp
        conversation.sort(key=lambda msg: msg["timestamp"])
        
        # Limit if specified
        if limit:
            conversation = conversation[-limit:]
        
        return conversation
    
    def get_agent_messages(
        self,
        agent_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get messages involving an agent.
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of messages to return
            
        Returns:
            List of messages involving the agent
        """
        # Filter messages involving the agent
        messages = [
            msg for msg in self.message_history
            if msg["from"] == agent_id or msg["to"] == agent_id
        ]
        
        # Sort by timestamp
        messages.sort(key=lambda msg: msg["timestamp"])
        
        # Limit if specified
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def clear_history(self) -> None:
        """Clear message history."""
        self.message_history = []
        logger.info(f"Cleared message history for coordinator '{self.name}'")
    
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """Get all registered agents.
        
        Returns:
            Dictionary mapping agent IDs to agent instances
        """
        return self.agents.copy()
    
    def coordinate_task(
        self,
        task: str,
        primary_agent_id: str,
        helper_agent_ids: List[str],
        max_rounds: int = 5
    ) -> Dict[str, Any]:
        """Coordinate a task between multiple agents.
        
        Args:
            task: Task description
            primary_agent_id: ID of the primary agent
            helper_agent_ids: IDs of helper agents
            max_rounds: Maximum number of rounds
            
        Returns:
            Final result from the primary agent
            
        Raises:
            ValueError: If agent not found
        """
        # Check if agents exist
        if primary_agent_id not in self.agents:
            raise ValueError(f"Primary agent '{primary_agent_id}' not found")
        
        for agent_id in helper_agent_ids:
            if agent_id not in self.agents:
                raise ValueError(f"Helper agent '{agent_id}' not found")
        
        # Start with the primary agent
        primary_agent = self.agents[primary_agent_id]
        result = primary_agent.process(task)
        
        # Initial response
        response = result["response"]
        
        # Coordinate rounds
        for round_num in range(max_rounds):
            # Check if we need help
            if "I need help" not in response.lower() and "I'm not sure" not in response.lower():
                # No help needed, we're done
                break
            
            # Ask helper agents for input
            helper_responses = []
            
            for agent_id in helper_agent_ids:
                helper_agent = self.agents[agent_id]
                
                # Create message for helper
                helper_message = f"The primary agent said: '{response}'\n\nCan you help with this task: {task}"
                
                # Send message to helper
                message_obj = self.send_message(
                    from_agent_id=primary_agent_id,
                    to_agent_id=agent_id,
                    message=helper_message
                )
                
                # Process message
                helper_response = self.process_message(message_obj)
                helper_responses.append(helper_response["message"])
            
            # Combine helper responses
            combined_help = "\n\n".join([
                f"Helper {i+1}: {resp}"
                for i, resp in enumerate(helper_responses)
            ])
            
            # Send combined help to primary agent
            primary_message = f"Here's input from the helper agents:\n\n{combined_help}\n\nBased on this help, please provide your final answer to the task: {task}"
            
            # Process with primary agent
            result = primary_agent.process(primary_message)
            response = result["response"]
        
        # Return final result
        return {
            "task": task,
            "primary_agent": primary_agent_id,
            "helper_agents": helper_agent_ids,
            "rounds": round_num + 1,
            "response": response,
            "full_result": result
        }
    
    async def coordinate_task_async(
        self,
        task: str,
        primary_agent_id: str,
        helper_agent_ids: List[str],
        max_rounds: int = 5
    ) -> Dict[str, Any]:
        """Coordinate a task between multiple agents asynchronously.
        
        Args:
            task: Task description
            primary_agent_id: ID of the primary agent
            helper_agent_ids: IDs of helper agents
            max_rounds: Maximum number of rounds
            
        Returns:
            Final result from the primary agent
            
        Raises:
            ValueError: If agent not found
        """
        # Check if agents exist
        if primary_agent_id not in self.agents:
            raise ValueError(f"Primary agent '{primary_agent_id}' not found")
        
        for agent_id in helper_agent_ids:
            if agent_id not in self.agents:
                raise ValueError(f"Helper agent '{agent_id}' not found")
        
        # Start with the primary agent
        primary_agent = self.agents[primary_agent_id]
        
        # Process with primary agent
        if hasattr(primary_agent, "process_async"):
            result = await primary_agent.process_async(task)
        else:
            # Run synchronous process in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: primary_agent.process(task)
            )
        
        # Initial response
        response = result["response"]
        
        # Coordinate rounds
        round_num = 0
        for round_num in range(max_rounds):
            # Check if we need help
            if "I need help" not in response.lower() and "I'm not sure" not in response.lower():
                # No help needed, we're done
                break
            
            # Ask helper agents for input
            helper_tasks = []
            
            for agent_id in helper_agent_ids:
                helper_agent = self.agents[agent_id]
                
                # Create message for helper
                helper_message = f"The primary agent said: '{response}'\n\nCan you help with this task: {task}"
                
                # Send message to helper
                message_obj = {
                    "id": str(uuid.uuid4()),
                    "from": primary_agent_id,
                    "to": agent_id,
                    "message": helper_message,
                    "metadata": {},
                    "timestamp": time.time()
                }
                
                # Add to history
                self.message_history.append(message_obj)
                
                # Process message asynchronously
                helper_tasks.append(self.process_message_async(message_obj))
            
            # Wait for all helper responses
            helper_responses = await asyncio.gather(*helper_tasks)
            
            # Combine helper responses
            combined_help = "\n\n".join([
                f"Helper {i+1}: {resp['message']}"
                for i, resp in enumerate(helper_responses)
            ])
            
            # Send combined help to primary agent
            primary_message = f"Here's input from the helper agents:\n\n{combined_help}\n\nBased on this help, please provide your final answer to the task: {task}"
            
            # Process with primary agent
            if hasattr(primary_agent, "process_async"):
                result = await primary_agent.process_async(primary_message)
            else:
                # Run synchronous process in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, lambda: primary_agent.process(primary_message)
                )
            
            response = result["response"]
        
        # Return final result
        return {
            "task": task,
            "primary_agent": primary_agent_id,
            "helper_agents": helper_agent_ids,
            "rounds": round_num + 1,
            "response": response,
            "full_result": result
        }
