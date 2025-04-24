"""
Tests for the CodePromptTemplates class.

These tests verify the functionality of the CodePromptTemplates class
for generating various code-related prompts.
"""

import pytest

from augment_adam.ai_agent.models.prompts import CodePromptTemplates

class TestCodePromptTemplates:
    """Tests for the CodePromptTemplates class."""
    
    # Sample code for testing
    SAMPLE_CODE = """
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count
"""
    
    def test_docstring_generation(self):
        """Test generating docstring prompts."""
        # Test with default style
        prompt = CodePromptTemplates.docstring_generation(self.SAMPLE_CODE)
        
        # Check that the prompt contains the expected elements
        assert "Google-style" in prompt
        assert self.SAMPLE_CODE in prompt
        
        # Test with different styles
        for style in ["google", "numpy", "sphinx"]:
            prompt = CodePromptTemplates.docstring_generation(self.SAMPLE_CODE, style)
            
            # Style-specific text should be in the prompt
            if style == "google":
                assert "Google-style" in prompt
            elif style == "numpy":
                assert "NumPy-style" in prompt
            elif style == "sphinx":
                assert "Sphinx-style" in prompt
    
    def test_test_generation(self):
        """Test generating test prompts."""
        # Test with default parameters
        prompt = CodePromptTemplates.test_generation(self.SAMPLE_CODE)
        
        # Check that the prompt contains the expected elements
        assert "pytest" in prompt
        assert "thorough test cases" in prompt
        assert self.SAMPLE_CODE in prompt
        
        # Test with different frameworks and coverage levels
        frameworks = ["pytest", "unittest"]
        coverage_levels = ["basic", "high", "comprehensive"]
        
        for framework in frameworks:
            for coverage in coverage_levels:
                prompt = CodePromptTemplates.test_generation(
                    self.SAMPLE_CODE, framework, coverage
                )
                
                # Framework should be in the prompt
                assert framework in prompt
                
                # Coverage level description should be in the prompt
                if coverage == "basic":
                    assert "basic test cases" in prompt
                elif coverage == "high":
                    assert "thorough test cases" in prompt
                elif coverage == "comprehensive":
                    assert "comprehensive test cases" in prompt
    
    def test_code_explanation(self):
        """Test generating code explanation prompts."""
        # Test with default detail level
        prompt = CodePromptTemplates.code_explanation(self.SAMPLE_CODE)
        
        # Check that the prompt contains the expected elements
        assert "a clear explanation with moderate detail" in prompt
        assert self.SAMPLE_CODE in prompt
        
        # Test with different detail levels
        detail_levels = ["brief", "medium", "detailed"]
        
        for level in detail_levels:
            prompt = CodePromptTemplates.code_explanation(self.SAMPLE_CODE, level)
            
            # Detail level description should be in the prompt
            if level == "brief":
                assert "a brief, high-level explanation" in prompt
            elif level == "medium":
                assert "a clear explanation with moderate detail" in prompt
            elif level == "detailed":
                assert "a detailed, line-by-line explanation" in prompt
    
    def test_code_review(self):
        """Test generating code review prompts."""
        # Test with default parameters
        prompt = CodePromptTemplates.code_review(self.SAMPLE_CODE)
        
        # Check that the prompt contains the expected elements
        assert "Review the following Python code" in prompt
        assert "list of findings" in prompt
        assert self.SAMPLE_CODE in prompt
        
        # Test with focus areas
        focus_areas = ["performance", "security", "style"]
        prompt = CodePromptTemplates.code_review(self.SAMPLE_CODE, focus_areas)
        
        # Focus areas should be in the prompt
        for area in focus_areas:
            assert area in prompt
    
    def test_code_completion(self):
        """Test generating code completion prompts."""
        task_description = "Calculate the median of a list of numbers"
        
        prompt = CodePromptTemplates.code_completion(self.SAMPLE_CODE, task_description)
        
        # Check that the prompt contains the expected elements
        assert "Complete the following Python code" in prompt
        assert task_description in prompt
        assert self.SAMPLE_CODE in prompt
    
    def test_refactoring(self):
        """Test generating refactoring prompts."""
        # Test with default goal
        prompt = CodePromptTemplates.refactoring(self.SAMPLE_CODE)
        
        # Check that the prompt contains the expected elements
        assert "Refactor the following Python code" in prompt
        assert "improve readability and clarity" in prompt
        assert self.SAMPLE_CODE in prompt
        
        # Test with different goals
        goals = ["readability", "performance", "maintainability", "security"]
        
        for goal in goals:
            prompt = CodePromptTemplates.refactoring(self.SAMPLE_CODE, goal)
            
            # Goal description should be in the prompt
            if goal == "readability":
                assert "improve readability and clarity" in prompt
            elif goal == "performance":
                assert "optimize performance" in prompt
            elif goal == "maintainability":
                assert "enhance maintainability and extensibility" in prompt
            elif goal == "security":
                assert "improve security and reduce vulnerabilities" in prompt
