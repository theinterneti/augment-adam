"""
Prompt templates for the AI coding agent.

This module provides specialized prompt templates for
code-related tasks such as documentation generation,
test creation, and code explanation.
"""

from typing import Dict, List, Optional, Union, Any
import re

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
