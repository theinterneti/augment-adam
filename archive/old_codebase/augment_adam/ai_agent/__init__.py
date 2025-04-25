"""AI Agent for the Augment Adam assistant.

This module provides a flexible AI agent architecture with model management,
memory integration, and reasoning capabilities.

Version: 0.1.0
Created: 2025-04-27
"""

from augment_adam.ai_agent.agent_interface import AgentInterface
from augment_adam.ai_agent.base_agent import BaseAgent
from augment_adam.ai_agent.agent_factory import AgentFactory, create_agent, get_default_agent

__all__ = [
    "AgentInterface",
    "BaseAgent",
    "AgentFactory",
    "create_agent",
    "get_default_agent",
]