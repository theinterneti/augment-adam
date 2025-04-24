"""Creative Agent for the AI Agent.

This module provides a creative-focused agent.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
import json
import random
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)
from augment_adam.ai_agent.base_agent import BaseAgent
from augment_adam.ai_agent.smc.potential import Potential, RegexPotential
from augment_adam.ai_agent.reasoning.reflection import Reflection

logger = logging.getLogger(__name__)


class CreativeAgent(BaseAgent):
    """Creative Agent for the AI Agent.
    
    This class provides a creative-focused agent.
    
    Attributes:
        reflection_engine: The reflection engine for creative reflection
        creative_modes: List of creative modes
        current_mode: The current creative mode
        style_templates: Dictionary of style templates
    """
    
    def __init__(
        self,
        name: str = "Creative Agent",
        description: str = "A creative-focused AI agent",
        memory_type: str = None,
        context_window_size: int = 4096,
        potentials: Optional[List[Potential]] = None,
        num_particles: int = 100
    ):
        """Initialize the Creative Agent.
        
        Args:
            name: The name of the agent
            description: A description of the agent
            memory_type: The type of memory to use (if None, use default)
            context_window_size: The size of the context window
            potentials: List of potential functions for controlled generation
            num_particles: Number of particles for SMC sampling
        """
        # Add creative-specific potentials
        if potentials is None:
            potentials = []
        
        # Add a regex potential for creative output
        creative_potential = RegexPotential(
            pattern=r".*\n.*\n.*",  # Matches text with at least 3 lines
            name="creative_potential"
        )
        potentials.append(creative_potential)
        
        # Initialize base agent
        super().__init__(
            name=name,
            description=description,
            memory_type=memory_type,
            context_window_size=context_window_size,
            potentials=potentials,
            num_particles=num_particles
        )
        
        # Initialize reflection engine
        self.reflection_engine = Reflection()
        
        # Initialize creative modes
        self.creative_modes = [
            "storytelling",
            "poetry",
            "brainstorming",
            "visual_description",
            "dialogue",
            "free_form"
        ]
        self.current_mode = "free_form"
        
        # Initialize style templates
        self.style_templates = {
            "storytelling": "Once upon a time, {input}...",
            "poetry": "{input}\nWords flowing like water\nThoughts dancing in the mind",
            "brainstorming": "Ideas for {input}:\n1. \n2. \n3. ",
            "visual_description": "Visualizing {input}:\n\nThe scene unfolds...",
            "dialogue": "Character 1: What do you think about {input}?\nCharacter 2: Well, I believe...",
            "free_form": "{input}"
        }
        
        logger.info(f"Initialized {name} with {len(self.creative_modes)} creative modes")
    
    def process(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process input and generate a creative response.
        
        Args:
            input_text: The input text to process
            context: Additional context for processing
            
        Returns:
            A dictionary containing the response and additional information
        """
        try:
            # Check for mode change request
            new_mode = self._check_mode_change(input_text)
            if new_mode:
                self.current_mode = new_mode
                mode_response = f"I've switched to {new_mode} mode. Let me create something for you in this style."
                
                return {
                    "response": mode_response,
                    "mode": self.current_mode
                }
            
            # Apply creative mode template
            template = self.style_templates.get(self.current_mode, "{input}")
            creative_prompt = template.replace("{input}", input_text)
            
            # Create context with creative information
            if context is None:
                context = {}
            context["creative_mode"] = self.current_mode
            context["creative_prompt"] = creative_prompt
            
            # Process with base agent
            result = super().process(creative_prompt, context)
            
            # Reflect on the creative output
            reflection = self.reflection_engine.reflect(
                result["response"],
                {"mode": self.current_mode, "input": input_text}
            )
            
            # Add creative information to result
            result["creative_mode"] = self.current_mode
            result["reflection"] = reflection
            
            return result
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to process creative input",
                category=ErrorCategory.RESOURCE,
                details={"input_length": len(input_text) if input_text else 0},
            )
            log_error(error, logger=logger)
            
            # Fall back to simple response
            return {
                "response": "I'm sorry, I encountered an error while processing your creative request.",
                "error": str(error)
            }
    
    def _check_mode_change(self, input_text: str) -> Optional[str]:
        """Check if the input requests a mode change.
        
        Args:
            input_text: The input text
            
        Returns:
            The new mode if requested, None otherwise
        """
        input_lower = input_text.lower()
        
        # Check for explicit mode change requests
        mode_keywords = {
            "storytelling": ["story", "tell me a story", "narrative", "fiction"],
            "poetry": ["poem", "poetry", "verse", "rhyme"],
            "brainstorming": ["brainstorm", "ideas", "suggestions", "options"],
            "visual_description": ["describe", "visual", "scene", "picture", "imagine"],
            "dialogue": ["dialogue", "conversation", "characters talking"],
            "free_form": ["free form", "freestyle", "no constraints"]
        }
        
        for mode, keywords in mode_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                return mode
        
        return None
    
    def generate_creative(
        self,
        prompt: str,
        mode: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1000
    ) -> str:
        """Generate creative text.
        
        Args:
            prompt: The prompt to generate from
            mode: The creative mode to use (if None, use current mode)
            constraints: Constraints for generation
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated creative text
        """
        try:
            # Use specified mode or current mode
            creative_mode = mode or self.current_mode
            
            # Apply creative mode template
            template = self.style_templates.get(creative_mode, "{input}")
            creative_prompt = template.replace("{input}", prompt)
            
            # Generate with base agent
            result = self.generate(
                prompt=creative_prompt,
                constraints=constraints,
                max_tokens=max_tokens
            )
            
            logger.info(f"Generated creative text in {creative_mode} mode")
            return result
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to generate creative text",
                category=ErrorCategory.RESOURCE,
                details={"prompt_length": len(prompt) if prompt else 0},
            )
            log_error(error, logger=logger)
            
            # Fall back to simple response
            return f"I'm sorry, I encountered an error while generating creative text for: {prompt}"
    
    def add_creative_mode(self, mode: str, template: str) -> None:
        """Add a new creative mode.
        
        Args:
            mode: The name of the mode
            template: The template for the mode
        """
        self.creative_modes.append(mode)
        self.style_templates[mode] = template
        logger.info(f"Added creative mode: {mode}")
    
    def get_creative_modes(self) -> List[str]:
        """Get the list of creative modes.
        
        Returns:
            The list of creative modes
        """
        return self.creative_modes
    
    def set_creative_mode(self, mode: str) -> bool:
        """Set the current creative mode.
        
        Args:
            mode: The mode to set
            
        Returns:
            True if the mode was set, False if the mode is not valid
        """
        if mode in self.creative_modes:
            self.current_mode = mode
            logger.info(f"Set creative mode to: {mode}")
            return True
        return False
