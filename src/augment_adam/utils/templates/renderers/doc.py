"""
Documentation renderer for the template engine.

This module provides a renderer for rendering templates to documentation.
"""

from typing import Dict, List, Any, Optional, Set, Union, Tuple

from augment_adam.utils.templates.core.template import Template, TemplateContext
from augment_adam.utils.templates.core.engine import TemplateEngine


class DocRenderer:
    """
    Renderer for rendering templates to documentation.
    
    This class provides methods for rendering templates to documentation,
    including Markdown, reStructuredText, and other documentation formats.
    
    Attributes:
        engine: The template engine to use for rendering.
    
    TODO(Issue #5): Add support for documentation validation
    TODO(Issue #5): Add support for documentation formatting
    """
    
    def __init__(self, engine: Optional[TemplateEngine] = None) -> None:
        """
        Initialize the documentation renderer.
        
        Args:
            engine: The template engine to use for rendering. If None, uses the default engine.
        """
        if engine is None:
            from augment_adam.utils.templates.core.engine import get_template_engine
            engine = get_template_engine()
        
        self.engine = engine
    
    def render_markdown(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to Markdown documentation.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered Markdown documentation.
        """
        return self.engine.render_template(f"docs/markdown/{template_name}", context)
    
    def render_rst(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to reStructuredText documentation.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered reStructuredText documentation.
        """
        return self.engine.render_template(f"docs/rst/{template_name}", context)
    
    def render_html_doc(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to HTML documentation.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered HTML documentation.
        """
        return self.engine.render_template(f"docs/html/{template_name}", context)
    
    def render_readme(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a README.md file.
        
        Args:
            context: Context to use for rendering the README.
            
        Returns:
            Rendered README.md file.
        """
        return self.render_markdown("readme.md.j2", context)
    
    def render_api_doc(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render API documentation.
        
        Args:
            context: Context to use for rendering the API documentation.
            
        Returns:
            Rendered API documentation.
        """
        return self.render_markdown("api.md.j2", context)
    
    def render_user_guide(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a user guide.
        
        Args:
            context: Context to use for rendering the user guide.
            
        Returns:
            Rendered user guide.
        """
        return self.render_markdown("user_guide.md.j2", context)
    
    def render_developer_guide(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a developer guide.
        
        Args:
            context: Context to use for rendering the developer guide.
            
        Returns:
            Rendered developer guide.
        """
        return self.render_markdown("developer_guide.md.j2", context)
