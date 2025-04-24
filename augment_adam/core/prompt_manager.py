"""Prompt management for the Dukat assistant.

This module handles the creation, storage, and optimization of prompts
for use with DSPy modules.

Version: 0.1.0
Created: 2025-04-22
"""

from typing import Dict, Any, List, Optional, Union
import logging
import os
import json
from pathlib import Path
import time

import dspy

logger = logging.getLogger(__name__)


class PromptTemplate:
    """A template for generating prompts.

    This class represents a template for generating prompts with
    variable substitution.

    Attributes:
        name: The name of the template.
        template: The template string.
        variables: The variables used in the template.
        description: A description of the template.
        created_at: The timestamp when the template was created.
        updated_at: The timestamp when the template was last updated.
    """

    def __init__(
        self,
        name: str,
        template: str,
        variables: Optional[List[str]] = None,
        description: str = "",
    ):
        """Initialize a prompt template.

        Args:
            name: The name of the template.
            template: The template string.
            variables: The variables used in the template.
            description: A description of the template.
        """
        self.name = name
        self.template = template
        self.variables = variables or []
        self.description = description
        self.created_at = int(time.time())
        self.updated_at = self.created_at

        # Extract variables from the template if not provided
        if not self.variables:
            self._extract_variables()

        logger.info(f"Initialized prompt template: {name}")

    def _extract_variables(self) -> None:
        """Extract variables from the template.

        This method extracts variables of the form {variable_name}
        from the template string.
        """
        import re

        # Find all patterns like {variable_name}
        pattern = r'\{([a-zA-Z0-9_]+)\}'
        matches = re.findall(pattern, self.template)

        # Store unique variable names
        self.variables = list(set(matches))

        logger.debug(f"Extracted variables from template: {self.variables}")

    def format(self, **kwargs) -> str:
        """Format the template with the given variables.

        Args:
            **kwargs: The variables to substitute in the template.

        Returns:
            The formatted prompt string.

        Raises:
            ValueError: If a required variable is missing.
        """
        # Check for missing variables
        missing = [var for var in self.variables if var not in kwargs]
        if missing:
            error_msg = f"Missing variables for template {self.name}: {missing}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Format the template
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            error_msg = f"Error formatting template {self.name}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the template to a dictionary.

        Returns:
            A dictionary representation of the template.
        """
        return {
            "name": self.name,
            "template": self.template,
            "variables": self.variables,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptTemplate":
        """Create a template from a dictionary.

        Args:
            data: A dictionary representation of the template.

        Returns:
            A new PromptTemplate instance.
        """
        template = cls(
            name=data["name"],
            template=data["template"],
            variables=data.get("variables", []),
            description=data.get("description", ""),
        )

        template.created_at = data.get("created_at", template.created_at)
        template.updated_at = data.get("updated_at", template.updated_at)

        return template


class PromptManager:
    """Manager for prompt templates.

    This class manages the creation, storage, and optimization of
    prompt templates for use with DSPy modules.

    Attributes:
        templates: Dictionary of prompt templates.
        persist_dir: Directory to persist templates.
    """

    def __init__(
        self,
        persist_dir: Optional[str] = None,
    ):
        """Initialize the prompt manager.

        Args:
            persist_dir: Directory to persist templates.
        """
        self.templates: Dict[str, PromptTemplate] = {}
        self.persist_dir = persist_dir or os.path.expanduser(
            "~/.augment_adam/prompts")

        # Create directory if it doesn't exist
        os.makedirs(self.persist_dir, exist_ok=True)

        # Load templates
        self._load_templates()

        # Initialize default templates if none exist
        if not self.templates:
            self._init_default_templates()

        logger.info(
            f"Initialized prompt manager with {len(self.templates)} templates")

    def _load_templates(self) -> None:
        """Load templates from the persist directory."""
        try:
            template_files = list(Path(self.persist_dir).glob("*.json"))

            for file_path in template_files:
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)

                    template = PromptTemplate.from_dict(data)
                    self.templates[template.name] = template

                    logger.debug(f"Loaded template from {file_path}")

                except Exception as e:
                    logger.error(
                        f"Error loading template from {file_path}: {str(e)}")

            logger.info(f"Loaded {len(self.templates)} templates")

        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")

    def _save_template(self, template: PromptTemplate) -> bool:
        """Save a template to the persist directory.

        Args:
            template: The template to save.

        Returns:
            True if successful, False otherwise.
        """
        try:
            file_path = os.path.join(self.persist_dir, f"{template.name}.json")

            with open(file_path, "w") as f:
                json.dump(template.to_dict(), f, indent=2)

            logger.debug(f"Saved template to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving template {template.name}: {str(e)}")
            return False

    def _init_default_templates(self) -> None:
        """Initialize default templates."""
        # Basic conversation template
        self.add_template(
            name="conversation",
            template=(
                "You are a helpful AI assistant named Dukat. "
                "You are designed to be helpful, harmless, and honest.\n\n"
                "Previous conversation:\n{history}\n\n"
                "User: {question}\n"
                "Dukat:"
            ),
            description="Basic conversation template",
        )

        # Chain of thought template
        self.add_template(
            name="chain_of_thought",
            template=(
                "You are a helpful AI assistant named Dukat. "
                "You are designed to be helpful, harmless, and honest.\n\n"
                "Previous conversation:\n{history}\n\n"
                "User: {question}\n\n"
                "Think through this step by step:\n"
                "1. Understand what the user is asking for\n"
                "2. Consider relevant information and context\n"
                "3. Formulate a clear and helpful response\n\n"
                "Dukat:"
            ),
            description="Chain of thought reasoning template",
        )

        # Tool use template
        self.add_template(
            name="tool_use",
            template=(
                "You are a helpful AI assistant named Dukat with access to tools. "
                "You can use tools to help answer the user's question.\n\n"
                "Available tools:\n{tools}\n\n"
                "Previous conversation:\n{history}\n\n"
                "User: {question}\n\n"
                "First, decide if you need to use a tool. If so, specify which tool "
                "and what parameters to use. If not, just answer directly.\n\n"
                "Dukat:"
            ),
            description="Template for tool use",
        )

        logger.info("Initialized default templates")

    def add_template(
        self,
        name: str,
        template: str,
        variables: Optional[List[str]] = None,
        description: str = "",
        overwrite: bool = False,
    ) -> bool:
        """Add a new template.

        Args:
            name: The name of the template.
            template: The template string.
            variables: The variables used in the template.
            description: A description of the template.
            overwrite: Whether to overwrite an existing template.

        Returns:
            True if successful, False otherwise.
        """
        if name in self.templates and not overwrite:
            logger.warning(f"Template {name} already exists")
            return False

        try:
            # Create the template
            template_obj = PromptTemplate(
                name=name,
                template=template,
                variables=variables,
                description=description,
            )

            # Store the template
            self.templates[name] = template_obj

            # Save the template
            self._save_template(template_obj)

            logger.info(f"Added template: {name}")
            return True

        except Exception as e:
            logger.error(f"Error adding template {name}: {str(e)}")
            return False

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name.

        Args:
            name: The name of the template.

        Returns:
            The template, or None if not found.
        """
        return self.templates.get(name)

    def format_prompt(self, template_name: str, **kwargs) -> str:
        """Format a prompt using a template.

        Args:
            template_name: The name of the template to use.
            **kwargs: The variables to substitute in the template.

        Returns:
            The formatted prompt string.

        Raises:
            ValueError: If the template is not found or a required variable is missing.
        """
        template = self.get_template(template_name)
        if template is None:
            error_msg = f"Template {template_name} not found"
            logger.error(error_msg)
            raise ValueError(error_msg)

        return template.format(**kwargs)

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all templates.

        Returns:
            A list of template information.
        """
        return [
            {
                "name": template.name,
                "description": template.description,
                "variables": template.variables,
                "created_at": template.created_at,
                "updated_at": template.updated_at,
            }
            for template in self.templates.values()
        ]

    def delete_template(self, name: str) -> bool:
        """Delete a template.

        Args:
            name: The name of the template to delete.

        Returns:
            True if successful, False otherwise.
        """
        if name not in self.templates:
            logger.warning(f"Template {name} not found")
            return False

        try:
            # Remove from memory
            del self.templates[name]

            # Remove from disk
            file_path = os.path.join(self.persist_dir, f"{name}.json")
            if os.path.exists(file_path):
                os.remove(file_path)

            logger.info(f"Deleted template: {name}")
            return True

        except Exception as e:
            logger.error(f"Error deleting template {name}: {str(e)}")
            return False

    def update_template(
        self,
        name: str,
        template: Optional[str] = None,
        variables: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> bool:
        """Update an existing template.

        Args:
            name: The name of the template to update.
            template: The new template string.
            variables: The new variables.
            description: The new description.

        Returns:
            True if successful, False otherwise.
        """
        if name not in self.templates:
            logger.warning(f"Template {name} not found")
            return False

        try:
            # Get the existing template
            template_obj = self.templates[name]

            # Update fields
            if template is not None:
                template_obj.template = template
                if variables is None:
                    template_obj._extract_variables()

            if variables is not None:
                template_obj.variables = variables

            if description is not None:
                template_obj.description = description

            # Update timestamp - ensure it's different from the original
            current_time = int(time.time())
            if current_time <= template_obj.updated_at:
                current_time = template_obj.updated_at + 1
            template_obj.updated_at = current_time

            # Save the template
            self._save_template(template_obj)

            logger.info(f"Updated template: {name}")
            return True

        except Exception as e:
            logger.error(f"Error updating template {name}: {str(e)}")
            return False

    def create_dspy_module(
        self,
        template_name: str,
        signature: str,
        module_type: str = "chain_of_thought",
    ) -> dspy.Module:
        """Create a DSPy module with a specific template.

        Args:
            template_name: The name of the template to use.
            signature: The signature for the DSPy module.
            module_type: The type of DSPy module to create.

        Returns:
            A DSPy module instance.

        Raises:
            ValueError: If the template is not found or the module type is invalid.
        """
        # Check if the template exists
        if template_name not in self.templates:
            error_msg = f"Template {template_name} not found"
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            # Create the appropriate module type
            if module_type.lower() == "chain_of_thought":
                return dspy.ChainOfThought(signature)
            elif module_type.lower() == "predict":
                return dspy.Predict(signature)
            elif module_type.lower() == "react":
                return dspy.ReAct(signature)
            else:
                error_msg = f"Invalid module type: {module_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        except ValueError as e:
            # Re-raise ValueError for invalid module type
            raise
        except Exception as e:
            error_msg = f"Error creating DSPy module: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)


# Singleton instance for easy access
default_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager(
    persist_dir: Optional[str] = None,
) -> PromptManager:
    """Get or create the default prompt manager instance.

    Args:
        persist_dir: Directory to persist templates.

    Returns:
        The default prompt manager instance.
    """
    global default_prompt_manager

    if default_prompt_manager is None:
        default_prompt_manager = PromptManager(persist_dir)

    return default_prompt_manager
