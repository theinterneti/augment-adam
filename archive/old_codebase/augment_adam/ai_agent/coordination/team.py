"""Agent Team Implementation.

This module provides the team class for organizing agents with specific roles.

Version: 0.1.0
Created: 2025-05-01
"""

import logging
import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional, Union, Callable

from augment_adam.ai_agent.base_agent import BaseAgent
from augment_adam.ai_agent.coordination.coordinator import AgentCoordinator

logger = logging.getLogger(__name__)


class AgentTeam:
    """Agent Team.
    
    This class organizes agents into a team with specific roles.
    
    Attributes:
        name: Name of the team
        description: Description of the team
        coordinator: Agent coordinator
        roles: Dictionary mapping role names to agent IDs
        role_descriptions: Dictionary mapping role names to descriptions
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        coordinator: Optional[AgentCoordinator] = None,
        roles: Optional[Dict[str, str]] = None,
        role_descriptions: Optional[Dict[str, str]] = None
    ):
        """Initialize the Agent Team.
        
        Args:
            name: Name of the team
            description: Description of the team
            coordinator: Agent coordinator
            roles: Dictionary mapping role names to agent IDs
            role_descriptions: Dictionary mapping role names to descriptions
        """
        self.name = name
        self.description = description
        self.coordinator = coordinator or AgentCoordinator(f"{name}_coordinator")
        self.roles = roles or {}
        self.role_descriptions = role_descriptions or {}
        
        logger.info(f"Initialized Agent Team '{name}' with {len(self.roles)} roles")
    
    def add_role(
        self,
        role_name: str,
        agent_id: str,
        description: str,
        agent: Optional[BaseAgent] = None
    ) -> None:
        """Add a role to the team.
        
        Args:
            role_name: Name of the role
            agent_id: ID of the agent
            description: Description of the role
            agent: Agent instance (if not already registered with coordinator)
        """
        # Register agent if provided
        if agent:
            self.coordinator.register_agent(agent_id, agent)
        
        # Add role
        self.roles[role_name] = agent_id
        self.role_descriptions[role_name] = description
        
        logger.info(f"Added role '{role_name}' to team '{self.name}'")
    
    def remove_role(self, role_name: str) -> bool:
        """Remove a role from the team.
        
        Args:
            role_name: Name of the role to remove
            
        Returns:
            True if role was removed, False otherwise
        """
        if role_name in self.roles:
            del self.roles[role_name]
            
            if role_name in self.role_descriptions:
                del self.role_descriptions[role_name]
            
            logger.info(f"Removed role '{role_name}' from team '{self.name}'")
            return True
        else:
            logger.warning(f"Role '{role_name}' not found in team '{self.name}'")
            return False
    
    def get_agent_for_role(self, role_name: str) -> Optional[BaseAgent]:
        """Get the agent for a role.
        
        Args:
            role_name: Name of the role
            
        Returns:
            Agent instance or None if not found
        """
        if role_name in self.roles:
            agent_id = self.roles[role_name]
            return self.coordinator.get_agent(agent_id)
        else:
            return None
    
    def get_role_for_agent(self, agent_id: str) -> Optional[str]:
        """Get the role for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Role name or None if not found
        """
        for role_name, role_agent_id in self.roles.items():
            if role_agent_id == agent_id:
                return role_name
        
        return None
    
    def send_message_to_role(
        self,
        from_role: str,
        to_role: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a message from one role to another.
        
        Args:
            from_role: Name of the sending role
            to_role: Name of the receiving role
            message: Message content
            metadata: Additional metadata
            
        Returns:
            Message object
            
        Raises:
            ValueError: If role not found
        """
        # Check if roles exist
        if from_role not in self.roles:
            raise ValueError(f"Role '{from_role}' not found")
        
        if to_role not in self.roles:
            raise ValueError(f"Role '{to_role}' not found")
        
        # Get agent IDs
        from_agent_id = self.roles[from_role]
        to_agent_id = self.roles[to_role]
        
        # Add role information to metadata
        role_metadata = metadata or {}
        role_metadata.update({
            "from_role": from_role,
            "to_role": to_role,
            "team": self.name
        })
        
        # Send message
        return self.coordinator.send_message(
            from_agent_id=from_agent_id,
            to_agent_id=to_agent_id,
            message=message,
            metadata=role_metadata
        )
    
    def process_message(
        self,
        message_obj: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a message.
        
        Args:
            message_obj: Message object
            context: Additional context
            
        Returns:
            Response from the receiving agent
        """
        return self.coordinator.process_message(message_obj, context)
    
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
        """
        return await self.coordinator.process_message_async(message_obj, context)
    
    def get_conversation_between_roles(
        self,
        role1: str,
        role2: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation between two roles.
        
        Args:
            role1: Name of the first role
            role2: Name of the second role
            limit: Maximum number of messages to return
            
        Returns:
            List of messages between the roles
            
        Raises:
            ValueError: If role not found
        """
        # Check if roles exist
        if role1 not in self.roles:
            raise ValueError(f"Role '{role1}' not found")
        
        if role2 not in self.roles:
            raise ValueError(f"Role '{role2}' not found")
        
        # Get agent IDs
        agent_id1 = self.roles[role1]
        agent_id2 = self.roles[role2]
        
        # Get conversation
        return self.coordinator.get_conversation(agent_id1, agent_id2, limit)
    
    def get_role_messages(
        self,
        role_name: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get messages involving a role.
        
        Args:
            role_name: Name of the role
            limit: Maximum number of messages to return
            
        Returns:
            List of messages involving the role
            
        Raises:
            ValueError: If role not found
        """
        # Check if role exists
        if role_name not in self.roles:
            raise ValueError(f"Role '{role_name}' not found")
        
        # Get agent ID
        agent_id = self.roles[role_name]
        
        # Get messages
        return self.coordinator.get_agent_messages(agent_id, limit)
    
    def execute_workflow(
        self,
        task: str,
        workflow: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a workflow.
        
        Args:
            task: Task description
            workflow: List of workflow steps
            context: Additional context
            
        Returns:
            Final result
            
        Raises:
            ValueError: If role not found
        """
        # Initialize context
        current_context = context or {}
        current_context["task"] = task
        current_context["results"] = []
        
        # Execute workflow steps
        for step in workflow:
            step_role = step["role"]
            step_action = step["action"]
            step_input = step.get("input", task)
            
            # Check if role exists
            if step_role not in self.roles:
                raise ValueError(f"Role '{step_role}' not found")
            
            # Get agent
            agent_id = self.roles[step_role]
            agent = self.coordinator.get_agent(agent_id)
            
            if not agent:
                raise ValueError(f"Agent for role '{step_role}' not found")
            
            # Format input with context
            formatted_input = step_input
            if isinstance(formatted_input, str):
                # Replace placeholders with context values
                for key, value in current_context.items():
                    if isinstance(value, str):
                        formatted_input = formatted_input.replace(f"{{{key}}}", value)
            
            # Execute action
            if step_action == "process":
                # Process with agent
                result = agent.process(formatted_input)
                
                # Update context
                current_context[f"{step_role}_result"] = result["response"]
                current_context["results"].append({
                    "role": step_role,
                    "action": step_action,
                    "input": formatted_input,
                    "output": result["response"]
                })
            elif step_action == "send_message":
                # Get recipient
                recipient_role = step.get("recipient")
                
                if not recipient_role:
                    raise ValueError(f"Recipient role not specified for send_message action")
                
                if recipient_role not in self.roles:
                    raise ValueError(f"Recipient role '{recipient_role}' not found")
                
                # Send message
                message_obj = self.send_message_to_role(
                    from_role=step_role,
                    to_role=recipient_role,
                    message=formatted_input
                )
                
                # Process message
                response = self.process_message(message_obj)
                
                # Update context
                current_context[f"{recipient_role}_response"] = response["message"]
                current_context["results"].append({
                    "role": step_role,
                    "action": step_action,
                    "recipient": recipient_role,
                    "input": formatted_input,
                    "output": response["message"]
                })
            else:
                raise ValueError(f"Unknown action '{step_action}'")
        
        # Return final context
        return current_context
    
    async def execute_workflow_async(
        self,
        task: str,
        workflow: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a workflow asynchronously.
        
        Args:
            task: Task description
            workflow: List of workflow steps
            context: Additional context
            
        Returns:
            Final result
            
        Raises:
            ValueError: If role not found
        """
        # Initialize context
        current_context = context or {}
        current_context["task"] = task
        current_context["results"] = []
        
        # Execute workflow steps
        for step in workflow:
            step_role = step["role"]
            step_action = step["action"]
            step_input = step.get("input", task)
            
            # Check if role exists
            if step_role not in self.roles:
                raise ValueError(f"Role '{step_role}' not found")
            
            # Get agent
            agent_id = self.roles[step_role]
            agent = self.coordinator.get_agent(agent_id)
            
            if not agent:
                raise ValueError(f"Agent for role '{step_role}' not found")
            
            # Format input with context
            formatted_input = step_input
            if isinstance(formatted_input, str):
                # Replace placeholders with context values
                for key, value in current_context.items():
                    if isinstance(value, str):
                        formatted_input = formatted_input.replace(f"{{{key}}}", value)
            
            # Execute action
            if step_action == "process":
                # Process with agent
                if hasattr(agent, "process_async"):
                    result = await agent.process_async(formatted_input)
                else:
                    # Run synchronous process in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None, lambda: agent.process(formatted_input)
                    )
                
                # Update context
                current_context[f"{step_role}_result"] = result["response"]
                current_context["results"].append({
                    "role": step_role,
                    "action": step_action,
                    "input": formatted_input,
                    "output": result["response"]
                })
            elif step_action == "send_message":
                # Get recipient
                recipient_role = step.get("recipient")
                
                if not recipient_role:
                    raise ValueError(f"Recipient role not specified for send_message action")
                
                if recipient_role not in self.roles:
                    raise ValueError(f"Recipient role '{recipient_role}' not found")
                
                # Send message
                message_obj = self.send_message_to_role(
                    from_role=step_role,
                    to_role=recipient_role,
                    message=formatted_input
                )
                
                # Process message
                response = await self.process_message_async(message_obj)
                
                # Update context
                current_context[f"{recipient_role}_response"] = response["message"]
                current_context["results"].append({
                    "role": step_role,
                    "action": step_action,
                    "recipient": recipient_role,
                    "input": formatted_input,
                    "output": response["message"]
                })
            else:
                raise ValueError(f"Unknown action '{step_action}'")
        
        # Return final context
        return current_context
    
    def get_team_info(self) -> Dict[str, Any]:
        """Get information about the team.
        
        Returns:
            Team information
        """
        return {
            "name": self.name,
            "description": self.description,
            "roles": {
                role_name: {
                    "agent_id": agent_id,
                    "description": self.role_descriptions.get(role_name, "")
                }
                for role_name, agent_id in self.roles.items()
            },
            "agents": {
                agent_id: agent.get_info() if hasattr(agent, "get_info") else {"name": agent.name}
                for agent_id, agent in self.coordinator.get_all_agents().items()
            }
        }
