"""
Agent Team Implementation.

This module provides the team class for organizing agents with specific roles.
"""

import logging
import uuid
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.ai_agent.coordination.coordinator import AgentCoordinator, get_agent_coordinator

logger = logging.getLogger(__name__)


@tag("ai_agent.coordination")
class AgentTeam:
    """
    Agent Team.

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
        """
        Initialize the Agent Team.

        Args:
            name: Name of the team
            description: Description of the team
            coordinator: Agent coordinator
            roles: Dictionary mapping role names to agent IDs
            role_descriptions: Dictionary mapping role names to descriptions
        """
        self.name = name
        self.description = description
        self.coordinator = coordinator or get_agent_coordinator()
        self.roles = roles or {}
        self.role_descriptions = role_descriptions or {}

        logger.info(f"Initialized Agent Team '{name}' with {len(self.roles)} roles")

    def add_role(
        self,
        role_name: str,
        agent_id: str,
        description: str,
        agent: Optional[Any] = None
    ) -> None:
        """
        Add a role to the team.

        Args:
            role_name: Name of the role
            agent_id: ID of the agent
            description: Description of the role
            agent: Agent instance (if not already registered with coordinator)
        """
        # Register agent if provided
        if agent:
            self.coordinator.registry.register_agent(agent_id, agent)

        # Add role
        self.roles[role_name] = agent_id
        self.role_descriptions[role_name] = description

        logger.info(f"Added role '{role_name}' to team '{self.name}'")

    def remove_role(self, role_name: str) -> bool:
        """
        Remove a role from the team.

        Args:
            role_name: Name of the role to remove

        Returns:
            True if the role was removed, False otherwise
        """
        if role_name in self.roles:
            del self.roles[role_name]
            if role_name in self.role_descriptions:
                del self.role_descriptions[role_name]
            logger.info(f"Removed role '{role_name}' from team '{self.name}'")
            return True
        return False

    def get_agent_for_role(self, role_name: str) -> Optional[Any]:
        """
        Get the agent for a role.

        Args:
            role_name: Name of the role

        Returns:
            Agent or None if the role doesn't exist
        """
        agent_id = self.roles.get(role_name)
        if not agent_id:
            return None

        return self.coordinator.get_agent(agent_id)

    def get_role_for_agent(self, agent_id: str) -> Optional[str]:
        """
        Get the role for an agent.

        Args:
            agent_id: ID of the agent

        Returns:
            Role name or None if the agent doesn't have a role
        """
        for role_name, role_agent_id in self.roles.items():
            if role_agent_id == agent_id:
                return role_name

        return None

    def send_message_to_role(
        self,
        from_role: str,
        to_role: str,
        message: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a message from one role to another.

        Args:
            from_role: Name of the sending role
            to_role: Name of the receiving role
            message: Message content
            metadata: Additional metadata for the message

        Returns:
            Message information
        """
        # Check that the roles exist
        if from_role not in self.roles:
            raise ValueError(f"Role '{from_role}' does not exist in team '{self.name}'")

        if to_role not in self.roles:
            raise ValueError(f"Role '{to_role}' does not exist in team '{self.name}'")

        # Get the agent IDs
        from_agent_id = self.roles[from_role]
        to_agent_id = self.roles[to_role]

        # Prepare metadata
        message_metadata = metadata or {}
        message_metadata.update({
            "from_role": from_role,
            "to_role": to_role,
            "team": self.name
        })

        # Send the message
        return self.coordinator.send_message(
            from_agent_id=from_agent_id,
            to_agent_id=to_agent_id,
            message=message,
            metadata=message_metadata
        )

    def process_message(self, message: Dict[str, Any], agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a message.

        Args:
            message: Message to process
            agent_id: ID of the agent to process the message, or None to use the coordinator

        Returns:
            Response message
        """
        return self.coordinator.process_message(message, agent_id)

    async def process_message_async(self, message: Dict[str, Any], agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a message asynchronously.

        Args:
            message: Message to process
            agent_id: ID of the agent to process the message, or None to use the coordinator

        Returns:
            Response message
        """
        return await self.coordinator.process_message_async(message, agent_id)

    def get_conversation_between_roles(
        self,
        role1: str,
        role2: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get the conversation between two roles.

        Args:
            role1: Name of the first role
            role2: Name of the second role
            limit: Maximum number of messages to return

        Returns:
            List of messages
        """
        # Check that the roles exist
        if role1 not in self.roles:
            raise ValueError(f"Role '{role1}' does not exist in team '{self.name}'")

        if role2 not in self.roles:
            raise ValueError(f"Role '{role2}' does not exist in team '{self.name}'")

        # Get the agent IDs
        agent1_id = self.roles[role1]
        agent2_id = self.roles[role2]

        # Get the conversation
        return self.coordinator.get_conversation(agent1_id, agent2_id, limit)

    def get_role_messages(self, role_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get messages involving a role.

        Args:
            role_name: Name of the role
            limit: Maximum number of messages to return

        Returns:
            List of messages
        """
        # Check that the role exists
        if role_name not in self.roles:
            raise ValueError(f"Role '{role_name}' does not exist in team '{self.name}'")

        # Get the agent ID
        agent_id = self.roles[role_name]

        # Get the messages
        return self.coordinator.get_agent_messages(agent_id, limit)

    def execute_workflow(self, task: Any, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a workflow with the team.

        Args:
            task: The task to execute
            workflow_steps: List of workflow step dictionaries

        Returns:
            Workflow execution results
        """
        results = []

        for step in workflow_steps:
            # Get the role and action
            role = step.get("role")
            action = step.get("action")

            # Check that the role exists
            if role not in self.roles:
                raise ValueError(f"Role '{role}' does not exist in team '{self.name}'")

            # Get the agent for the role
            agent = self.get_agent_for_role(role)

            # Create a result for this step
            result = {
                "role": role,
                "action": action,
                "input": step.get("input", "")
            }

            # Process the step based on the action
            if action == "process":
                # Process the input with the agent
                output = agent.process(step.get("input", ""))
                result["output"] = output.get("response") if isinstance(output, dict) else output

            elif action == "send_message":
                # Check that the recipient is specified
                recipient = step.get("recipient")
                if not recipient:
                    raise ValueError(f"No recipient specified for send_message action in step for role '{role}'")

                # Check that the recipient exists
                if recipient not in self.roles:
                    raise ValueError(f"Recipient role '{recipient}' does not exist in team '{self.name}'")

                # Add recipient to the result
                result["recipient"] = recipient

                # Send the message
                message = self.send_message_to_role(
                    from_role=role,
                    to_role=recipient,
                    message=step.get("input", "")
                )

                # Process the message
                response = self.process_message(message)
                result["output"] = response.get("message") if isinstance(response, dict) else response

            else:
                raise ValueError(f"Unknown action '{action}' in step for role '{role}'")

            results.append(result)

        return {
            "task": task,
            "results": results,
            "status": "completed"
        }

    async def execute_workflow_async(self, task: Any, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a workflow with the team asynchronously.

        Args:
            task: The task to execute
            workflow_steps: List of workflow step dictionaries

        Returns:
            Workflow execution results
        """
        results = []

        for step in workflow_steps:
            # Get the role and action
            role = step.get("role")
            action = step.get("action")

            # Check that the role exists
            if role not in self.roles:
                raise ValueError(f"Role '{role}' does not exist in team '{self.name}'")

            # Get the agent for the role
            agent = self.get_agent_for_role(role)

            # Create a result for this step
            result = {
                "role": role,
                "action": action,
                "input": step.get("input", "")
            }

            # Process the step based on the action
            if action == "process":
                # Process the input with the agent asynchronously
                output = await agent.process_async(step.get("input", ""))
                result["output"] = output.get("response") if isinstance(output, dict) else output

            elif action == "send_message":
                # Check that the recipient is specified
                recipient = step.get("recipient")
                if not recipient:
                    raise ValueError(f"No recipient specified for send_message action in step for role '{role}'")

                # Check that the recipient exists
                if recipient not in self.roles:
                    raise ValueError(f"Recipient role '{recipient}' does not exist in team '{self.name}'")

                # Add recipient to the result
                result["recipient"] = recipient

                # Send the message
                message = self.send_message_to_role(
                    from_role=role,
                    to_role=recipient,
                    message=step.get("input", "")
                )

                # Process the message asynchronously
                response = await self.process_message_async(message)
                result["output"] = response.get("message") if isinstance(response, dict) else response

            else:
                raise ValueError(f"Unknown action '{action}' in step for role '{role}'")

            results.append(result)

        return {
            "task": task,
            "results": results,
            "status": "completed"
        }

    def get_team_info(self) -> Dict[str, Any]:
        """
        Get information about the team.

        Returns:
            Team information
        """
        # Get all agents
        agents = self.coordinator.get_all_agents()

        # Build agent info
        agent_info = {}
        for agent_id, agent in agents.items():
            if agent_id in self.roles.values():
                agent_info[agent_id] = agent.get_info()

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
            "agents": agent_info
        }
