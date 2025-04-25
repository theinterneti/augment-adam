"""
Test renderer for the template engine.

This module provides a renderer for rendering templates to tests.
"""

from typing import Dict, List, Any, Optional, Set, Union, Tuple

from augment_adam.utils.templates.core.template import Template, TemplateContext
from augment_adam.utils.templates.core.engine import TemplateEngine


class TestRenderer:
    """
    Renderer for rendering templates to tests.
    
    This class provides methods for rendering templates to tests,
    including unit tests, integration tests, and other test types.
    
    Attributes:
        engine: The template engine to use for rendering.
    
    TODO(Issue #5): Add support for test validation
    TODO(Issue #5): Add support for test formatting
    """
    
    def __init__(self, engine: Optional[TemplateEngine] = None) -> None:
        """
        Initialize the test renderer.
        
        Args:
            engine: The template engine to use for rendering. If None, uses the default engine.
        """
        if engine is None:
            from augment_adam.utils.templates.core.engine import get_template_engine
            engine = get_template_engine()
        
        self.engine = engine
    
    def render_unit_test(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to a unit test.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered unit test.
        """
        return self.engine.render_template(f"tests/unit/{template_name}", context)
    
    def render_integration_test(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to an integration test.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered integration test.
        """
        return self.engine.render_template(f"tests/integration/{template_name}", context)
    
    def render_e2e_test(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to an end-to-end test.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered end-to-end test.
        """
        return self.engine.render_template(f"tests/e2e/{template_name}", context)
    
    def render_class_test(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a test for a Python class.
        
        Args:
            context: Context to use for rendering the test.
            
        Returns:
            Rendered class test.
        """
        return self.render_unit_test("class_test.py.j2", context)
    
    def render_function_test(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a test for a Python function.
        
        Args:
            context: Context to use for rendering the test.
            
        Returns:
            Rendered function test.
        """
        return self.render_unit_test("function_test.py.j2", context)
    
    def render_module_test(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a test for a Python module.
        
        Args:
            context: Context to use for rendering the test.
            
        Returns:
            Rendered module test.
        """
        return self.render_unit_test("module_test.py.j2", context)
