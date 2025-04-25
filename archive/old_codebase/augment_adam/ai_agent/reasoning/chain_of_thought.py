"""Chain of Thought Reasoning.

This module implements chain of thought reasoning.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)

logger = logging.getLogger(__name__)


class ChainOfThought:
    """Chain of Thought Reasoning.

    This class implements chain of thought reasoning.

    Attributes:
        model: The model to use for reasoning
        max_steps: Maximum number of reasoning steps
        step_template: Template for each reasoning step
    """

    def __init__(
        self,
        model: Any = None,
        max_steps: int = 5,
        step_template: Optional[str] = None
    ):
        """Initialize Chain of Thought.

        Args:
            model: The model to use for reasoning
            max_steps: Maximum number of reasoning steps
            step_template: Template for each reasoning step
        """
        self.model = model
        self.max_steps = max_steps

        # Set default step template if not provided
        if step_template:
            self.step_template = step_template
        else:
            self.step_template = (
                "Step {step_number}: {step_description}\n"
                "Reasoning: {reasoning}\n"
                "Intermediate conclusion: {conclusion}\n"
            )

        logger.info("Initialized Chain of Thought reasoning")

    def reason(
        self,
        query: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform chain of thought reasoning.

        Args:
            query: The query to reason about
            context: Additional context for reasoning

        Returns:
            The reasoning results
        """
        try:
            if self.model:
                # Create a prompt for chain of thought reasoning
                prompt = self._create_reasoning_prompt(query, context)

                # Generate reasoning using the model
                reasoning_text = self.model.generate(
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.7,
                    stop=["Final Answer:", "\n\n\n"]
                )

                # Parse the reasoning
                steps, conclusion = self._parse_reasoning(reasoning_text)
            else:
                # Fallback if no model is available
                logger.warning("No model available for reasoning, using placeholder")

                # Generate placeholder reasoning steps
                steps = []
                for i in range(3):  # Simplified to 3 steps
                    step = {
                        "step_number": i + 1,
                        "step_description": f"Consider aspect {i + 1}",
                        "reasoning": f"Reasoning for step {i + 1}",
                        "conclusion": f"Conclusion for step {i + 1}"
                    }
                    steps.append(step)

                # Generate placeholder conclusion
                conclusion = "Final conclusion based on the reasoning steps."

            # Create result
            result = {
                "query": query,
                "steps": steps,
                "conclusion": conclusion
            }

            logger.info(f"Performed chain of thought reasoning with {len(steps)} steps")
            return result
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to perform chain of thought reasoning",
                category=ErrorCategory.RESOURCE,
                details={"query": query},
            )
            log_error(error, logger=logger)

            # Return minimal result
            return {
                "query": query,
                "steps": [],
                "conclusion": "Unable to perform reasoning due to an error."
            }

    def _create_reasoning_prompt(self, query: str, context: Optional[str] = None) -> str:
        """Create a prompt for chain of thought reasoning.

        Args:
            query: The query to reason about
            context: Additional context for reasoning

        Returns:
            The reasoning prompt
        """
        prompt = "You are an expert at solving problems through careful step-by-step reasoning.\n\n"

        if context:
            prompt += f"Context:\n{context}\n\n"

        prompt += f"Question: {query}\n\n"
        prompt += "Let's think through this step by step:\n"

        return prompt

    def _parse_reasoning(self, reasoning_text: str) -> Tuple[List[Dict[str, Any]], str]:
        """Parse reasoning text into steps and conclusion.

        Args:
            reasoning_text: The reasoning text

        Returns:
            A tuple of (steps, conclusion)
        """
        # Split the reasoning text into lines
        lines = reasoning_text.strip().split("\n")

        # Initialize variables
        steps = []
        current_step = None
        conclusion = ""

        # Parse the reasoning text
        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check if this is a step
            if line.startswith("Step ") or line.startswith("1.") or line.startswith("1)"):
                # Save the previous step if it exists
                if current_step:
                    steps.append(current_step)

                # Create a new step
                current_step = {
                    "step_number": len(steps) + 1,
                    "step_description": line,
                    "reasoning": "",
                    "conclusion": ""
                }
            # Check if this is a conclusion
            elif line.startswith("Therefore") or line.startswith("In conclusion") or line.startswith("Final conclusion"):
                # Save the previous step if it exists
                if current_step:
                    steps.append(current_step)
                    current_step = None

                # Set the conclusion
                conclusion = line
            # Otherwise, add to the current step
            elif current_step:
                # If the line starts with "Conclusion" or "So", it's likely a step conclusion
                if line.startswith("Conclusion") or line.startswith("So"):
                    current_step["conclusion"] = line
                else:
                    # Otherwise, it's part of the reasoning
                    if current_step["reasoning"]:
                        current_step["reasoning"] += " " + line
                    else:
                        current_step["reasoning"] = line

        # Save the last step if it exists
        if current_step:
            steps.append(current_step)

        # If no conclusion was found, create one from the last step
        if not conclusion and steps:
            conclusion = f"Based on the reasoning, {steps[-1].get('conclusion', '')}"

        return steps, conclusion

    def format_reasoning(self, reasoning_result: Dict[str, Any]) -> str:
        """Format reasoning result as text.

        Args:
            reasoning_result: The reasoning result

        Returns:
            The formatted reasoning
        """
        try:
            # Format query
            formatted = f"Query: {reasoning_result['query']}\n\n"

            # Format steps
            for step in reasoning_result.get("steps", []):
                formatted += self.step_template.format(
                    step_number=step.get("step_number", ""),
                    step_description=step.get("step_description", ""),
                    reasoning=step.get("reasoning", ""),
                    conclusion=step.get("conclusion", "")
                )
                formatted += "\n"

            # Format conclusion
            formatted += f"Final conclusion: {reasoning_result.get('conclusion', '')}"

            return formatted
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to format reasoning",
                category=ErrorCategory.RESOURCE,
                details={},
            )
            log_error(error, logger=logger)

            # Return minimal formatting
            return f"Query: {reasoning_result.get('query', '')}\nConclusion: {reasoning_result.get('conclusion', '')}"
