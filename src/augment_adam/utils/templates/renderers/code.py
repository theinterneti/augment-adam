"""
Code renderer for the template engine.

This module provides a renderer for rendering templates to code.
"""

from typing import Dict, List, Any, Optional, Set, Union, Tuple

from augment_adam.utils.templates.core.template import Template, TemplateContext
from augment_adam.utils.templates.core.engine import TemplateEngine


class CodeRenderer:
    """
    Renderer for rendering templates to code.
    
    This class provides methods for rendering templates to code,
    including Python, JavaScript, and other programming languages.
    
    Attributes:
        engine: The template engine to use for rendering.
    
    TODO(Issue #5): Add support for code formatting
    TODO(Issue #5): Add support for code validation
    """
    
    def __init__(self, engine: Optional[TemplateEngine] = None) -> None:
        """
        Initialize the code renderer.
        
        Args:
            engine: The template engine to use for rendering. If None, uses the default engine.
        """
        if engine is None:
            from augment_adam.utils.templates.core.engine import get_template_engine
            engine = get_template_engine()
        
        self.engine = engine
    
    def render_python(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to Python code.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered Python code.
        """
        return self.engine.render_template(f"code/python/{template_name}", context)
    
    def render_javascript(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to JavaScript code.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered JavaScript code.
        """
        return self.engine.render_template(f"code/javascript/{template_name}", context)
    
    def render_html(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to HTML code.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered HTML code.
        """
        return self.engine.render_template(f"code/html/{template_name}", context)
    
    def render_css(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to CSS code.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered CSS code.
        """
        return self.engine.render_template(f"code/css/{template_name}", context)
    
    def render_sql(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to SQL code.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered SQL code.
        """
        return self.engine.render_template(f"code/sql/{template_name}", context)
    
    def render_yaml(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to YAML code.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered YAML code.
        """
        return self.engine.render_template(f"code/yaml/{template_name}", context)
    
    def render_json(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to JSON code.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered JSON code.
        """
        return self.engine.render_template(f"code/json/{template_name}", context)
    
    def render_class(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a Python class.
        
        Args:
            context: Context to use for rendering the class.
            
        Returns:
            Rendered Python class.
        """
        return self.render_python("class.py.j2", context)
    
    def render_function(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a Python function.
        
        Args:
            context: Context to use for rendering the function.
            
        Returns:
            Rendered Python function.
        """
        return self.render_python("function.py.j2", context)
    
    def render_module(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a Python module.
        
        Args:
            context: Context to use for rendering the module.
            
        Returns:
            Rendered Python module.
        """
        return self.render_python("module.py.j2", context)
