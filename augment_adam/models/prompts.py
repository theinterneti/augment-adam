"""
Prompt templates for the AI coding agent.

This module provides specialized prompt templates for
code-related tasks such as documentation generation,
test creation, and code explanation.

Version: 0.1.0
Created: 2025-04-22
Updated: 2025-04-24
"""

from typing import Dict, List, Optional, Union, Any, Callable
import re
import logging

logger = logging.getLogger(__name__)

class CodePromptTemplates:
    """
    Specialized prompt templates for code-related tasks.

    This class provides templates for common code generation,
    documentation, and testing tasks.
    """

    @staticmethod
    def docstring_generation(
        code: str,
        style: str = "google"
    ) -> str:
        """
        Generate a prompt for docstring generation.

        Args:
            code: The code to document
            style: Docstring style (google, numpy, sphinx)

        Returns:
            str: Formatted prompt
        """
        styles = {
            "google": "Google-style (https://google.github.io/styleguide/pyguide.html)",
            "numpy": "NumPy-style (https://numpydoc.readthedocs.io/en/latest/format.html)",
            "sphinx": "Sphinx-style (https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html)"
        }

        style_desc = styles.get(style, styles["google"])

        return f"""Generate a comprehensive {style_desc} docstring for the following Python code.
Include descriptions for all parameters, return values, raised exceptions, and examples if appropriate.
Only return the docstring, nothing else.

```python
{code}
```"""

    @staticmethod
    def test_generation(
        code: str,
        framework: str = "pytest",
        coverage_level: str = "high"
    ) -> str:
        """
        Generate a prompt for test case generation.

        Args:
            code: The code to test
            framework: Testing framework (pytest, unittest)
            coverage_level: Desired coverage level (basic, high, comprehensive)

        Returns:
            str: Formatted prompt
        """
        coverage_desc = {
            "basic": "basic test cases covering the main functionality",
            "high": "thorough test cases with good coverage of edge cases",
            "comprehensive": "comprehensive test cases with exhaustive coverage"
        }

        return f"""Generate {coverage_desc.get(coverage_level, "thorough")} {framework} tests for the following Python code.
Include tests for both normal operation and edge cases.
Make sure to test all public methods and functions.
Return only the test code, nothing else.

```python
{code}
```"""

    @staticmethod
    def code_explanation(
        code: str,
        detail_level: str = "medium"
    ) -> str:
        """
        Generate a prompt for code explanation.

        Args:
            code: The code to explain
            detail_level: Level of detail (brief, medium, detailed)

        Returns:
            str: Formatted prompt
        """
        detail_desc = {
            "brief": "a brief, high-level explanation",
            "medium": "a clear explanation with moderate detail",
            "detailed": "a detailed, line-by-line explanation"
        }

        return f"""Provide {detail_desc.get(detail_level, "a clear explanation with moderate detail")} of the following Python code.
Explain the purpose, functionality, and any important patterns or techniques used.

```python
{code}
```"""

    @staticmethod
    def code_review(
        code: str,
        focus_areas: Optional[List[str]] = None
    ) -> str:
        """
        Generate a prompt for code review.

        Args:
            code: The code to review
            focus_areas: Specific areas to focus on (performance, security, style, etc.)

        Returns:
            str: Formatted prompt
        """
        focus_str = ""
        if focus_areas:
            focus_str = f"Focus particularly on these areas: {', '.join(focus_areas)}.\n"

        return f"""Review the following Python code and provide constructive feedback.
Identify potential issues, bugs, and areas for improvement.
{focus_str}Format your response as a list of findings, each with:
1. Issue description
2. Severity (High/Medium/Low)
3. Suggested improvement

```python
{code}
```"""

    @staticmethod
    def code_completion(
        code: str,
        task_description: str
    ) -> str:
        """
        Generate a prompt for code completion.

        Args:
            code: The partial code to complete
            task_description: Description of what the code should do

        Returns:
            str: Formatted prompt
        """
        return f"""Complete the following Python code according to this task description:
{task_description}

Here's the partial code:
```python
{code}
```

Provide the completed code, making sure it fulfills the requirements.
Only return the complete code, nothing else."""

    @staticmethod
    def refactoring(
        code: str,
        goal: str = "readability"
    ) -> str:
        """
        Generate a prompt for code refactoring.

        Args:
            code: The code to refactor
            goal: Refactoring goal (readability, performance, maintainability)

        Returns:
            str: Formatted prompt
        """
        goals = {
            "readability": "improve readability and clarity",
            "performance": "optimize performance",
            "maintainability": "enhance maintainability and extensibility",
            "security": "improve security and reduce vulnerabilities"
        }

        goal_desc = goals.get(goal, goals["readability"])

        return f"""Refactor the following Python code to {goal_desc}.
Maintain the same functionality while improving the code quality.
Provide the refactored code along with a brief explanation of the changes made.

```python
{code}
```"""


class PromptTemplate:
    """A template for generating prompts.

    This class provides a way to create reusable prompt templates
    with variable substitution.

    Attributes:
        template: The template string with placeholders.
        variables: The variables to substitute in the template.
    """

    def __init__(self, template: str, variables: Optional[Dict[str, Any]] = None):
        """Initialize a prompt template.

        Args:
            template: The template string with placeholders.
            variables: Initial variables to substitute in the template.
        """
        self.template = template
        self.variables = variables or {}
        logger.debug(f"Created prompt template with {len(self.variables)} variables")

    def format(self, **kwargs) -> str:
        """Format the template with the given variables.

        Args:
            **kwargs: Variables to substitute in the template.

        Returns:
            The formatted prompt.
        """
        # Combine initial variables with provided kwargs
        variables = {**self.variables, **kwargs}

        try:
            # Format the template with the variables
            return self.template.format(**variables)
        except KeyError as e:
            logger.error(f"Missing variable in prompt template: {e}")
            # Return template with missing variables marked
            return f"ERROR: Missing variable {e} in prompt template"
        except Exception as e:
            logger.error(f"Error formatting prompt template: {e}")
            return f"ERROR: {str(e)}"

    def __call__(self, **kwargs) -> str:
        """Call the template with the given variables.

        This allows the template to be used as a function.

        Args:
            **kwargs: Variables to substitute in the template.

        Returns:
            The formatted prompt.
        """
        return self.format(**kwargs)


class PromptManager:
    """Manager for prompt templates.

    This class provides a way to manage and retrieve prompt templates.

    Attributes:
        templates: Dictionary of registered templates.
    """

    def __init__(self):
        """Initialize the prompt manager."""
        self.templates: Dict[str, PromptTemplate] = {}
        logger.debug("Initialized prompt manager")

    def register(self, name: str, template: Union[str, PromptTemplate]) -> None:
        """Register a prompt template.

        Args:
            name: The name of the template.
            template: The template string or PromptTemplate object.
        """
        if isinstance(template, str):
            template = PromptTemplate(template)

        self.templates[name] = template
        logger.debug(f"Registered prompt template: {name}")

    def get(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name.

        Args:
            name: The name of the template.

        Returns:
            The prompt template, or None if not found.
        """
        template = self.templates.get(name)
        if template is None:
            logger.warning(f"Prompt template not found: {name}")

        return template

    def format(self, name: str, **kwargs) -> Optional[str]:
        """Format a prompt template with the given variables.

        Args:
            name: The name of the template.
            **kwargs: Variables to substitute in the template.

        Returns:
            The formatted prompt, or None if the template is not found.
        """
        template = self.get(name)
        if template is None:
            return None

        return template.format(**kwargs)