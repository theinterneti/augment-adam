"""
Workflow Implementation.

This module provides classes for defining agent workflows.
"""

import logging
from typing import Dict, List, Any, Optional

from augment_adam.utils.tagging import tag

logger = logging.getLogger(__name__)


@tag("ai_agent.coordination")
class WorkflowStep:
    """
    Workflow Step.

    This class represents a step in a workflow.

    Attributes:
        role: Role that executes the step
        action: Action to perform
        input: Input for the step
        recipient: Recipient role (for send_message action)
        description: Description of the step
    """
    def __init__(
        self,
        role: str,
        action: str,
        input: Optional[str] = None,
        recipient: Optional[str] = None,
        description: Optional[str] = None
    ):
        """
        Initialize the Workflow Step.

        Args:
            role: Role that executes the step
            action: Action to perform
            input: Input for the step
            recipient: Recipient role (for send_message action)
            description: Description of the step
        """
        self.role = role
        self.action = action
        self.input = input
        self.recipient = recipient
        self.description = description

        # Validate action
        if action not in ["process", "send_message"]:
            raise ValueError(f"Unknown action '{action}'")

        # Validate recipient for send_message action
        if action == "send_message" and not recipient:
            raise ValueError("Recipient role not specified for send_message action")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dictionary representation
        """
        result = {
            "role": self.role,
            "action": self.action,
        }

        if self.input is not None:
            result["input"] = self.input

        if self.recipient is not None:
            result["recipient"] = self.recipient

        if self.description is not None:
            result["description"] = self.description

        return result


@tag("ai_agent.coordination")
class Workflow:
    """
    Workflow.

    This class represents a workflow of agent steps.

    Attributes:
        name: Name of the workflow
        description: Description of the workflow
        steps: List of workflow steps
    """
    def __init__(
        self,
        name: str,
        description: str,
        steps: Optional[List[WorkflowStep]] = None
    ):
        """
        Initialize the Workflow.

        Args:
            name: Name of the workflow
            description: Description of the workflow
            steps: List of workflow steps
        """
        self.name = name
        self.description = description
        self.steps = steps or []

        logger.info(f"Initialized Workflow '{name}' with {len(self.steps)} steps")

    def add_step(self, step: WorkflowStep) -> None:
        """
        Add a step to the workflow.

        Args:
            step: Workflow step
        """
        self.steps.append(step)
        logger.info(f"Added step to workflow '{self.name}'")

    def add_process_step(
        self,
        role: str,
        input: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """
        Add a process step to the workflow.

        Args:
            role: Role that executes the step
            input: Input for the step
            description: Description of the step
        """
        step = WorkflowStep(
            role=role,
            action="process",
            input=input,
            description=description
        )

        self.add_step(step)

    def add_message_step(
        self,
        from_role: str,
        to_role: str,
        message: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """
        Add a message step to the workflow.

        Args:
            from_role: Role that sends the message
            to_role: Role that receives the message
            message: Message content
            description: Description of the step
        """
        step = WorkflowStep(
            role=from_role,
            action="send_message",
            input=message,
            recipient=to_role,
            description=description
        )

        self.add_step(step)

    def to_list(self) -> List[Dict[str, Any]]:
        """
        Convert to list of dictionaries.

        Returns:
            List of step dictionaries
        """
        return [step.to_dict() for step in self.steps]

    @classmethod
    def from_list(
        cls,
        name: str,
        description: str,
        steps: List[Dict[str, Any]]
    ) -> "Workflow":
        """
        Create a workflow from a list of dictionaries.

        Args:
            name: Name of the workflow
            description: Description of the workflow
            steps: List of step dictionaries

        Returns:
            Workflow instance
        """
        workflow = cls(name=name, description=description)

        for step_dict in steps:
            step = WorkflowStep(
                role=step_dict["role"],
                action=step_dict["action"],
                input=step_dict.get("input"),
                recipient=step_dict.get("recipient"),
                description=step_dict.get("description")
            )

            workflow.add_step(step)

        return workflow
