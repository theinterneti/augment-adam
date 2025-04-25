"""Agent Types for the AI Agent.

This module provides different types of agents for different purposes.

Version: 0.1.0
Created: 2025-04-27
"""

from augment_adam.ai_agent.types.conversational_agent import ConversationalAgent
from augment_adam.ai_agent.types.task_agent import TaskAgent
from augment_adam.ai_agent.types.research_agent import ResearchAgent
from augment_adam.ai_agent.types.creative_agent import CreativeAgent
from augment_adam.ai_agent.types.coding_agent import CodingAgent

__all__ = [
    "ConversationalAgent",
    "TaskAgent",
    "ResearchAgent",
    "CreativeAgent",
    "CodingAgent",
]
