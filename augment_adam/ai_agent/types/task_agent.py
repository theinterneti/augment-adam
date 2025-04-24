"""Task Agent for the AI Agent.

This module provides a task-focused agent.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)
from augment_adam.ai_agent.base_agent import BaseAgent
from augment_adam.ai_agent.smc.potential import Potential, RegexPotential
from augment_adam.ai_agent.reasoning.planning import Planning

logger = logging.getLogger(__name__)


class TaskAgent(BaseAgent):
    """Task Agent for the AI Agent.
    
    This class provides a task-focused agent.
    
    Attributes:
        planning_engine: The planning engine for task planning
        current_task: The current task being worked on
        task_history: History of completed tasks
    """
    
    def __init__(
        self,
        name: str = "Task Agent",
        description: str = "A task-focused AI agent",
        memory_type: str = None,
        context_window_size: int = 4096,
        potentials: Optional[List[Potential]] = None,
        num_particles: int = 100
    ):
        """Initialize the Task Agent.
        
        Args:
            name: The name of the agent
            description: A description of the agent
            memory_type: The type of memory to use (if None, use default)
            context_window_size: The size of the context window
            potentials: List of potential functions for controlled generation
            num_particles: Number of particles for SMC sampling
        """
        # Add task-specific potentials
        if potentials is None:
            potentials = []
        
        # Add a regex potential for structured output
        structured_output_potential = RegexPotential(
            pattern=r".*\n(- .*\n)+.*",  # Matches lists with bullet points
            name="structured_output_potential"
        )
        potentials.append(structured_output_potential)
        
        # Initialize base agent
        super().__init__(
            name=name,
            description=description,
            memory_type=memory_type,
            context_window_size=context_window_size,
            potentials=potentials,
            num_particles=num_particles
        )
        
        # Initialize planning engine
        self.planning_engine = Planning()
        
        # Initialize task tracking
        self.current_task = None
        self.task_history = []
        
        logger.info(f"Initialized {name} with planning capabilities")
    
    def process(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process input and generate a response.
        
        Args:
            input_text: The input text to process
            context: Additional context for processing
            
        Returns:
            A dictionary containing the response and additional information
        """
        try:
            # Check if this is a new task
            is_new_task = self._is_new_task(input_text)
            
            # If this is a new task, create a plan
            if is_new_task:
                # Complete previous task if exists
                if self.current_task:
                    self.task_history.append(self.current_task)
                
                # Create a new task
                self.current_task = {
                    "description": input_text,
                    "plan": self._create_plan(input_text),
                    "status": "in_progress",
                    "steps_completed": 0,
                    "steps_total": 0
                }
                
                # Count total steps
                self.current_task["steps_total"] = len(self.current_task["plan"]["steps"])
                
                # Create context with task information
                if context is None:
                    context = {}
                context["task"] = self.current_task
                
                # Generate response with the plan
                plan_text = self._format_plan(self.current_task["plan"])
                response_prefix = f"I'll help you with that task. Here's my plan:\n\n{plan_text}\n\nLet's start with the first step."
                
                # Process with base agent
                result = super().process(input_text, context)
                
                # Combine response with plan
                result["response"] = response_prefix
                result["task"] = self.current_task
                
                return result
            
            # If this is a continuation of the current task
            elif self.current_task:
                # Update context with task information
                if context is None:
                    context = {}
                context["task"] = self.current_task
                
                # Process with base agent
                result = super().process(input_text, context)
                
                # Update task progress
                self._update_task_progress(input_text)
                
                # Add task information to result
                result["task"] = self.current_task
                
                return result
            
            # If there's no current task, process normally
            else:
                return super().process(input_text, context)
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to process task",
                category=ErrorCategory.RESOURCE,
                details={"input_length": len(input_text) if input_text else 0},
            )
            log_error(error, logger=logger)
            
            # Fall back to simple response
            return {
                "response": "I'm sorry, I encountered an error while processing your task.",
                "error": str(error)
            }
    
    def _is_new_task(self, input_text: str) -> bool:
        """Check if the input is a new task.
        
        Args:
            input_text: The input text to check
            
        Returns:
            True if the input is a new task, False otherwise
        """
        # This is a simple heuristic, in a real implementation use more sophisticated detection
        task_keywords = ["can you", "please", "help me", "I need", "create", "make", "build"]
        
        # Check if the input contains task keywords
        if any(keyword in input_text.lower() for keyword in task_keywords):
            # If there's no current task, it's a new task
            if not self.current_task:
                return True
            
            # If the input is significantly different from the current task, it's a new task
            if self.current_task and len(input_text) > 20:
                similarity = self._calculate_similarity(input_text, self.current_task["description"])
                if similarity < 0.5:  # Threshold for new task
                    return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts.
        
        Args:
            text1: The first text
            text2: The second text
            
        Returns:
            The similarity score (0-1)
        """
        # This is a simple Jaccard similarity, in a real implementation use embeddings
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _create_plan(self, task_description: str) -> Dict[str, Any]:
        """Create a plan for a task.
        
        Args:
            task_description: The task description
            
        Returns:
            The plan
        """
        # Use the planning engine to create a plan
        plan = self.planning_engine.create_plan(task_description)
        
        logger.info(f"Created plan with {len(plan['steps'])} steps for task: {task_description[:50]}...")
        return plan
    
    def _format_plan(self, plan: Dict[str, Any]) -> str:
        """Format a plan as text.
        
        Args:
            plan: The plan to format
            
        Returns:
            The formatted plan
        """
        formatted = f"Plan: {plan['description']}\n\n"
        
        for i, step in enumerate(plan["steps"]):
            formatted += f"{i+1}. {step['description']}\n"
        
        return formatted
    
    def _update_task_progress(self, input_text: str) -> None:
        """Update task progress based on input.
        
        Args:
            input_text: The input text
        """
        if not self.current_task:
            return
        
        # Simple heuristic: increment steps completed if input suggests progress
        progress_keywords = ["done", "completed", "finished", "next", "step", "continue"]
        
        if any(keyword in input_text.lower() for keyword in progress_keywords):
            self.current_task["steps_completed"] += 1
            
            # Check if all steps are completed
            if self.current_task["steps_completed"] >= self.current_task["steps_total"]:
                self.current_task["status"] = "completed"
                self.task_history.append(self.current_task)
                self.current_task = None
                
                logger.info("Task completed and moved to history")
    
    def get_current_task(self) -> Optional[Dict[str, Any]]:
        """Get the current task.
        
        Returns:
            The current task, or None if there's no current task
        """
        return self.current_task
    
    def get_task_history(self) -> List[Dict[str, Any]]:
        """Get the task history.
        
        Returns:
            The task history
        """
        return self.task_history
