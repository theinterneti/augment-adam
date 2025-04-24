"""Agent Factory for the AI Agent.

This module provides a factory for creating different types of agents.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, ValidationError, wrap_error, log_error, ErrorCategory
)
from augment_adam.ai_agent.base_agent import BaseAgent
from augment_adam.ai_agent.types.conversational_agent import ConversationalAgent
from augment_adam.ai_agent.types.task_agent import TaskAgent
from augment_adam.ai_agent.types.research_agent import ResearchAgent
from augment_adam.ai_agent.types.creative_agent import CreativeAgent
from augment_adam.ai_agent.types.coding_agent import CodingAgent
from augment_adam.ai_agent.smc.potential import Potential, GrammarPotential, RegexPotential

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating different types of agents.

    This class provides methods for creating different types of agents.

    Attributes:
        agent_types: Dictionary of agent types
    """

    def __init__(self):
        """Initialize the Agent Factory."""
        self.agent_types = {
            "base": BaseAgent,
            "conversational": ConversationalAgent,
            "task": TaskAgent,
            "research": ResearchAgent,
            "creative": CreativeAgent,
            "coding": CodingAgent
        }

        logger.info("Initialized Agent Factory")

    def create_agent(
        self,
        agent_type: str = "base",
        name: Optional[str] = None,
        description: Optional[str] = None,
        memory_type: Optional[str] = None,
        model_type: Optional[str] = None,
        model_name: Optional[str] = None,
        context_window_size: int = 4096,
        potentials: Optional[List[Potential]] = None,
        num_particles: int = 100,
        **kwargs
    ) -> BaseAgent:
        """Create an agent.

        Args:
            agent_type: The type of agent to create
            name: The name of the agent
            description: A description of the agent
            memory_type: The type of memory to use
            model_type: The type of model to use (if None, use default)
            model_name: The name of the model to use (if None, use default)
            context_window_size: The size of the context window
            potentials: List of potential functions for controlled generation
            num_particles: Number of particles for SMC sampling
            **kwargs: Additional arguments for the agent

        Returns:
            The created agent

        Raises:
            ValidationError: If the agent type is not supported
        """
        try:
            # Get agent class
            agent_class = self.agent_types.get(agent_type)
            if not agent_class:
                raise ValidationError(
                    message=f"Unsupported agent type: {agent_type}",
                    details={"supported_types": list(self.agent_types.keys())}
                )

            # Set default name and description if not provided
            if not name:
                name = f"{agent_type.capitalize()} Agent"

            if not description:
                description = f"A {agent_type} AI agent"

            # Create agent
            agent = agent_class(
                name=name,
                description=description,
                memory_type=memory_type,
                model_type=model_type,
                model_name=model_name,
                context_window_size=context_window_size,
                potentials=potentials,
                num_particles=num_particles,
                **kwargs
            )

            logger.info(f"Created {agent_type} agent: {name}")
            return agent
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Failed to create {agent_type} agent",
                category=ErrorCategory.VALIDATION,
                details={"agent_type": agent_type},
            )
            log_error(error, logger=logger)

            # Fall back to base agent
            return BaseAgent(
                name=name or "Fallback Agent",
                description=description or "A fallback AI agent"
            )


# Global instance for singleton pattern
_agent_factory = None


def get_agent_factory() -> AgentFactory:
    """Get the global Agent Factory instance.

    Returns:
        The global Agent Factory instance
    """
    global _agent_factory

    if _agent_factory is None:
        _agent_factory = AgentFactory()

    return _agent_factory


def create_agent(
    agent_type: str = "base",
    name: Optional[str] = None,
    description: Optional[str] = None,
    memory_type: Optional[str] = None,
    model_type: Optional[str] = None,
    model_name: Optional[str] = None,
    context_window_size: int = 4096,
    potentials: Optional[List[Potential]] = None,
    num_particles: int = 100,
    **kwargs
) -> BaseAgent:
    """Create an agent using the global Agent Factory.

    Args:
        agent_type: The type of agent to create
        name: The name of the agent
        description: A description of the agent
        memory_type: The type of memory to use
        model_type: The type of model to use (if None, use default)
        model_name: The name of the model to use (if None, use default)
        context_window_size: The size of the context window
        potentials: List of potential functions for controlled generation
        num_particles: Number of particles for SMC sampling
        **kwargs: Additional arguments for the agent

    Returns:
        The created agent
    """
    factory = get_agent_factory()
    return factory.create_agent(
        agent_type=agent_type,
        name=name,
        description=description,
        memory_type=memory_type,
        model_type=model_type,
        model_name=model_name,
        context_window_size=context_window_size,
        potentials=potentials,
        num_particles=num_particles,
        **kwargs
    )


# Default agent instance
_default_agent = None


def get_default_agent() -> BaseAgent:
    """Get the default agent instance.

    Returns:
        The default agent instance
    """
    global _default_agent

    if _default_agent is None:
        _default_agent = create_agent(
            agent_type="conversational",
            name="Default Agent",
            description="The default AI agent"
        )

    return _default_agent
