"""Coding Agent for the AI Agent.

This module provides a code-focused agent.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)
from augment_adam.ai_agent.base_agent import BaseAgent
from augment_adam.ai_agent.smc.potential import Potential, GrammarPotential
from augment_adam.ai_agent.reasoning.decision_making import DecisionMaking

logger = logging.getLogger(__name__)


class CodingAgent(BaseAgent):
    """Coding Agent for the AI Agent.
    
    This class provides a code-focused agent.
    
    Attributes:
        decision_engine: The decision engine for code-related decisions
        supported_languages: List of supported programming languages
        language_grammars: Dictionary of language grammars
        current_language: The current programming language
    """
    
    def __init__(
        self,
        name: str = "Coding Agent",
        description: str = "A code-focused AI agent",
        memory_type: str = None,
        context_window_size: int = 4096,
        potentials: Optional[List[Potential]] = None,
        num_particles: int = 100,
        supported_languages: Optional[List[str]] = None
    ):
        """Initialize the Coding Agent.
        
        Args:
            name: The name of the agent
            description: A description of the agent
            memory_type: The type of memory to use (if None, use default)
            context_window_size: The size of the context window
            potentials: List of potential functions for controlled generation
            num_particles: Number of particles for SMC sampling
            supported_languages: List of supported programming languages
        """
        # Set default supported languages if not provided
        if supported_languages:
            self.supported_languages = supported_languages
        else:
            self.supported_languages = [
                "python",
                "javascript",
                "typescript",
                "java",
                "c",
                "cpp",
                "csharp",
                "go",
                "rust",
                "ruby",
                "php",
                "swift",
                "kotlin"
            ]
        
        # Initialize language grammars (placeholder)
        self.language_grammars = {}
        self._initialize_language_grammars()
        
        # Set default language
        self.current_language = "python"
        
        # Add code-specific potentials
        if potentials is None:
            potentials = []
        
        # Add a grammar potential for the current language
        grammar = self.language_grammars.get(self.current_language)
        if grammar:
            code_potential = GrammarPotential(
                grammar=grammar,
                name=f"{self.current_language}_grammar_potential"
            )
            potentials.append(code_potential)
        
        # Initialize base agent
        super().__init__(
            name=name,
            description=description,
            memory_type=memory_type,
            context_window_size=context_window_size,
            potentials=potentials,
            num_particles=num_particles
        )
        
        # Initialize decision engine
        self.decision_engine = DecisionMaking()
        
        logger.info(f"Initialized {name} with {len(self.supported_languages)} supported languages")
    
    def _initialize_language_grammars(self) -> None:
        """Initialize language grammars."""
        # This is a placeholder for actual grammar initialization
        # In a real implementation, use proper grammar definitions
        
        # Simple placeholder grammars
        for language in self.supported_languages:
            self.language_grammars[language] = f"{language}_grammar"
    
    def process(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process input and generate a code-focused response.
        
        Args:
            input_text: The input text to process
            context: Additional context for processing
            
        Returns:
            A dictionary containing the response and additional information
        """
        try:
            # Detect language in input
            detected_language = self._detect_language(input_text)
            if detected_language and detected_language != self.current_language:
                self._switch_language(detected_language)
            
            # Detect code task
            code_task = self._detect_code_task(input_text)
            
            # Create context with code information
            if context is None:
                context = {}
            context["language"] = self.current_language
            context["code_task"] = code_task
            
            # Process with base agent
            result = super().process(input_text, context)
            
            # Extract code from response
            code_blocks = self._extract_code_blocks(result["response"])
            
            # Make decisions about the code
            if code_blocks:
                decisions = self.decision_engine.make_decisions(
                    code_blocks[0],
                    {"language": self.current_language, "task": code_task}
                )
                result["decisions"] = decisions
            
            # Add code information to result
            result["language"] = self.current_language
            result["code_task"] = code_task
            result["code_blocks"] = code_blocks
            
            return result
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to process code request",
                category=ErrorCategory.RESOURCE,
                details={"input_length": len(input_text) if input_text else 0},
            )
            log_error(error, logger=logger)
            
            # Fall back to simple response
            return {
                "response": "I'm sorry, I encountered an error while processing your code request.",
                "error": str(error)
            }
    
    def _detect_language(self, input_text: str) -> Optional[str]:
        """Detect programming language in input.
        
        Args:
            input_text: The input text
            
        Returns:
            The detected language, or None if no language is detected
        """
        input_lower = input_text.lower()
        
        # Check for explicit language mentions
        for language in self.supported_languages:
            if language in input_lower or f"{language} code" in input_lower:
                return language
        
        # Check for file extensions
        extensions = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin"
        }
        
        for ext, language in extensions.items():
            if ext in input_lower:
                return language
        
        return None
    
    def _switch_language(self, language: str) -> None:
        """Switch to a different programming language.
        
        Args:
            language: The language to switch to
        """
        if language not in self.supported_languages:
            logger.warning(f"Unsupported language: {language}")
            return
        
        # Update current language
        self.current_language = language
        
        # Update grammar potential
        grammar = self.language_grammars.get(language)
        if grammar:
            # Remove existing grammar potentials
            self.potentials = [p for p in self.potentials if not isinstance(p, GrammarPotential)]
            
            # Add new grammar potential
            code_potential = GrammarPotential(
                grammar=grammar,
                name=f"{language}_grammar_potential"
            )
            self.potentials.append(code_potential)
            
            # Update SMC sampler
            self.smc_sampler.update_potentials(self.potentials)
        
        logger.info(f"Switched to language: {language}")
    
    def _detect_code_task(self, input_text: str) -> str:
        """Detect the code task in input.
        
        Args:
            input_text: The input text
            
        Returns:
            The detected code task
        """
        input_lower = input_text.lower()
        
        # Check for common code tasks
        if any(word in input_lower for word in ["implement", "create", "write", "code"]):
            return "implementation"
        elif any(word in input_lower for word in ["debug", "fix", "error", "issue"]):
            return "debugging"
        elif any(word in input_lower for word in ["optimize", "performance", "faster", "efficient"]):
            return "optimization"
        elif any(word in input_lower for word in ["explain", "understand", "how does", "what does"]):
            return "explanation"
        elif any(word in input_lower for word in ["test", "unit test", "testing"]):
            return "testing"
        else:
            return "general"
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from text.
        
        Args:
            text: The text to extract code blocks from
            
        Returns:
            The extracted code blocks
        """
        # Extract code blocks enclosed in triple backticks
        pattern = r"```(?:\w+)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        # If no matches, check for indented code blocks
        if not matches:
            lines = text.split("\n")
            code_block = []
            in_block = False
            
            for line in lines:
                if line.startswith("    ") or line.startswith("\t"):
                    in_block = True
                    code_block.append(line.lstrip())
                elif in_block and not line.strip():
                    code_block.append("")
                elif in_block:
                    matches.append("\n".join(code_block))
                    code_block = []
                    in_block = False
            
            if in_block:
                matches.append("\n".join(code_block))
        
        return matches
    
    def generate_code(
        self,
        prompt: str,
        language: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1000
    ) -> str:
        """Generate code based on a prompt.
        
        Args:
            prompt: The prompt to generate code from
            language: The programming language to use (if None, use current language)
            constraints: Constraints for generation
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated code
        """
        try:
            # Use specified language or current language
            code_language = language or self.current_language
            
            # Switch language if needed
            if code_language != self.current_language:
                self._switch_language(code_language)
            
            # Create code prompt
            code_prompt = f"Generate {code_language} code for: {prompt}"
            
            # Generate with base agent
            result = self.generate(
                prompt=code_prompt,
                constraints=constraints,
                max_tokens=max_tokens
            )
            
            # Extract code blocks
            code_blocks = self._extract_code_blocks(result)
            
            # Return first code block or full result
            if code_blocks:
                logger.info(f"Generated {code_language} code")
                return code_blocks[0]
            else:
                logger.info(f"Generated text (no code block detected)")
                return result
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to generate code",
                category=ErrorCategory.RESOURCE,
                details={"prompt_length": len(prompt) if prompt else 0},
            )
            log_error(error, logger=logger)
            
            # Fall back to simple response
            return f"# Error generating code\n# {str(error)}"
    
    def add_language(self, language: str, grammar: Any) -> None:
        """Add a new supported language.
        
        Args:
            language: The name of the language
            grammar: The grammar for the language
        """
        self.supported_languages.append(language)
        self.language_grammars[language] = grammar
        logger.info(f"Added supported language: {language}")
    
    def get_supported_languages(self) -> List[str]:
        """Get the list of supported languages.
        
        Returns:
            The list of supported languages
        """
        return self.supported_languages
