# Documentation System API

## Overview

The Documentation System provides a comprehensive API for generating, building, and managing documentation for the project. This document describes the main classes and functions in the Documentation System.

## Modules

### augment_adam.docs

The main module for the Documentation System.

```python
from augment_adam.docs import (
    DocGenerator,
    ModuleDocGenerator,
    ClassDocGenerator,
    FunctionDocGenerator,
    DocBuilder,
    MarkdownBuilder,
    HtmlBuilder,
    WebsiteBuilder,
    DocParser,
    DocFormatter,
    DocExtractor,
    DocValidator,
)
```

## Generators

### DocGenerator

Base class for documentation generators.

```python
class DocGenerator:
    def __init__(self, output_dir: str, template: Optional[Any] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the documentation generator.
        
        Args:
            output_dir: The directory to output documentation files to.
            template: The template to use for generating documentation.
            metadata: Additional metadata for the generator.
        """
        pass
    
    def generate(self, source: Any) -> Dict[str, Any]:
        """
        Generate documentation from a source.
        
        Args:
            source: The source to generate documentation from.
            
        Returns:
            Dictionary of documentation data.
        """
        pass
    
    def save(self, data: Dict[str, Any], output_file: str) -> None:
        """
        Save documentation data to a file.
        
        Args:
            data: The documentation data to save.
            output_file: The file to save the documentation to.
        """
        pass
    
    def generate_and_save(self, source: Any, output_file: str) -> Dict[str, Any]:
        """
        Generate documentation from a source and save it to a file.
        
        Args:
            source: The source to generate documentation from.
            output_file: The file to save the documentation to.
            
        Returns:
            Dictionary of documentation data.
        """
        pass
```

### ModuleDocGenerator

Generator for module documentation.

```python
class ModuleDocGenerator(DocGenerator):
    def __init__(
        self,
        output_dir: str,
        template: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        include_private: bool = False,
        include_dunder: bool = False
    ) -> None:
        """
        Initialize the module documentation generator.
        
        Args:
            output_dir: The directory to output documentation files to.
            template: The template to use for generating documentation.
            metadata: Additional metadata for the generator.
            include_private: Whether to include private members in the documentation.
            include_dunder: Whether to include dunder methods in the documentation.
        """
        pass
    
    def generate(self, source: Union[str, Any]) -> Dict[str, Any]:
        """
        Generate documentation for a module.
        
        Args:
            source: The module to generate documentation for, either as a module object or a module name.
            
        Returns:
            Dictionary of module documentation data.
        """
        pass
```

### ClassDocGenerator

Generator for class documentation.

```python
class ClassDocGenerator(DocGenerator):
    def __init__(
        self,
        output_dir: str,
        template: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        include_private: bool = False,
        include_dunder: bool = False
    ) -> None:
        """
        Initialize the class documentation generator.
        
        Args:
            output_dir: The directory to output documentation files to.
            template: The template to use for generating documentation.
            metadata: Additional metadata for the generator.
            include_private: Whether to include private members in the documentation.
            include_dunder: Whether to include dunder methods in the documentation.
        """
        pass
    
    def generate(self, source: Type) -> Dict[str, Any]:
        """
        Generate documentation for a class.
        
        Args:
            source: The class to generate documentation for.
            
        Returns:
            Dictionary of class documentation data.
        """
        pass
```

### FunctionDocGenerator

Generator for function documentation.

```python
class FunctionDocGenerator(DocGenerator):
    def __init__(
        self,
        output_dir: str,
        template: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the function documentation generator.
        
        Args:
            output_dir: The directory to output documentation files to.
            template: The template to use for generating documentation.
            metadata: Additional metadata for the generator.
        """
        pass
    
    def generate(self, source: Callable) -> Dict[str, Any]:
        """
        Generate documentation for a function.
        
        Args:
            source: The function to generate documentation for.
            
        Returns:
            Dictionary of function documentation data.
        """
        pass
```

## Builders

### DocBuilder

Base class for documentation builders.

```python
class DocBuilder:
    def __init__(
        self,
        output_dir: str,
        template_dir: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the documentation builder.
        
        Args:
            output_dir: The directory to output documentation files to.
            template_dir: The directory containing templates.
            metadata: Additional metadata for the builder.
        """
        pass
    
    def build(self, data: Dict[str, Any], output_file: str) -> None:
        """
        Build documentation from data.
        
        Args:
            data: The documentation data to build from.
            output_file: The file to save the documentation to.
        """
        pass
    
    def build_all(self, data_list: List[Dict[str, Any]], output_dir: str) -> None:
        """
        Build documentation for multiple data items.
        
        Args:
            data_list: The list of documentation data to build from.
            output_dir: The directory to save the documentation to.
        """
        pass
```

### MarkdownBuilder

Builder for Markdown documentation.

```python
class MarkdownBuilder(DocBuilder):
    def __init__(
        self,
        output_dir: str,
        template_dir: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        template: Optional[Any] = None
    ) -> None:
        """
        Initialize the Markdown builder.
        
        Args:
            output_dir: The directory to output documentation files to.
            template_dir: The directory containing templates.
            metadata: Additional metadata for the builder.
            template: The template to use for generating documentation.
        """
        pass
```

### HtmlBuilder

Builder for HTML documentation.

```python
class HtmlBuilder(DocBuilder):
    def __init__(
        self,
        output_dir: str,
        template_dir: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        template: Optional[Any] = None,
        css_file: Optional[str] = None,
        js_file: Optional[str] = None
    ) -> None:
        """
        Initialize the HTML builder.
        
        Args:
            output_dir: The directory to output documentation files to.
            template_dir: The directory containing templates.
            metadata: Additional metadata for the builder.
            template: The template to use for generating documentation.
            css_file: The CSS file to include in the HTML.
            js_file: The JavaScript file to include in the HTML.
        """
        pass
```

### WebsiteBuilder

Builder for documentation website.

```python
class WebsiteBuilder(DocBuilder):
    def __init__(
        self,
        output_dir: str,
        template_dir: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        title: str = "Documentation",
        description: str = "Documentation for the project",
        theme: str = "default"
    ) -> None:
        """
        Initialize the website builder.
        
        Args:
            output_dir: The directory to output documentation files to.
            template_dir: The directory containing templates.
            metadata: Additional metadata for the builder.
            title: The title of the website.
            description: The description of the website.
            theme: The theme to use for the website.
        """
        pass
```

## Utilities

### DocParser

Parser for documentation.

```python
class DocParser:
    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the documentation parser.
        
        Args:
            metadata: Additional metadata for the parser.
        """
        pass
    
    def parse_docstring(self, docstring: str) -> Dict[str, Any]:
        """
        Parse a docstring.
        
        Args:
            docstring: The docstring to parse.
            
        Returns:
            Dictionary of parsed documentation data.
        """
        pass
    
    def parse_markdown(self, markdown: str) -> Dict[str, Any]:
        """
        Parse Markdown documentation.
        
        Args:
            markdown: The Markdown documentation to parse.
            
        Returns:
            Dictionary of parsed documentation data.
        """
        pass
    
    def parse_rst(self, rst: str) -> Dict[str, Any]:
        """
        Parse reStructuredText documentation.
        
        Args:
            rst: The reStructuredText documentation to parse.
            
        Returns:
            Dictionary of parsed documentation data.
        """
        pass
```

### DocFormatter

Formatter for documentation.

```python
class DocFormatter:
    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the documentation formatter.
        
        Args:
            metadata: Additional metadata for the formatter.
        """
        pass
    
    def format_markdown(self, data: Dict[str, Any]) -> str:
        """
        Format documentation data as Markdown.
        
        Args:
            data: The documentation data to format.
            
        Returns:
            Formatted Markdown documentation.
        """
        pass
    
    def format_rst(self, data: Dict[str, Any]) -> str:
        """
        Format documentation data as reStructuredText.
        
        Args:
            data: The documentation data to format.
            
        Returns:
            Formatted reStructuredText documentation.
        """
        pass
    
    def format_html(self, data: Dict[str, Any]) -> str:
        """
        Format documentation data as HTML.
        
        Args:
            data: The documentation data to format.
            
        Returns:
            Formatted HTML documentation.
        """
        pass
```

### DocExtractor

Extractor for documentation.

```python
class DocExtractor:
    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the documentation extractor.
        
        Args:
            metadata: Additional metadata for the extractor.
        """
        pass
    
    def extract_module(self, module: Union[str, Any]) -> Dict[str, Any]:
        """
        Extract documentation from a module.
        
        Args:
            module: The module to extract documentation from, either as a module object or a module name.
            
        Returns:
            Dictionary of module documentation data.
        """
        pass
    
    def extract_class(self, cls: Type) -> Dict[str, Any]:
        """
        Extract documentation from a class.
        
        Args:
            cls: The class to extract documentation from.
            
        Returns:
            Dictionary of class documentation data.
        """
        pass
    
    def extract_function(self, func: Callable) -> Dict[str, Any]:
        """
        Extract documentation from a function.
        
        Args:
            func: The function to extract documentation from.
            
        Returns:
            Dictionary of function documentation data.
        """
        pass
    
    def extract_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract documentation from a Python file.
        
        Args:
            file_path: The path to the Python file.
            
        Returns:
            Dictionary of file documentation data.
        """
        pass
```

### DocValidator

Validator for documentation.

```python
class DocValidator:
    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the documentation validator.
        
        Args:
            metadata: Additional metadata for the validator.
        """
        pass
    
    def validate_docstring(self, docstring: str) -> List[str]:
        """
        Validate a docstring.
        
        Args:
            docstring: The docstring to validate.
            
        Returns:
            List of validation error messages.
        """
        pass
    
    def validate_module_doc(self, module_doc: Dict[str, Any]) -> List[str]:
        """
        Validate module documentation.
        
        Args:
            module_doc: The module documentation to validate.
            
        Returns:
            List of validation error messages.
        """
        pass
    
    def validate_class_doc(self, class_doc: Dict[str, Any]) -> List[str]:
        """
        Validate class documentation.
        
        Args:
            class_doc: The class documentation to validate.
            
        Returns:
            List of validation error messages.
        """
        pass
    
    def validate_function_doc(self, function_doc: Dict[str, Any]) -> List[str]:
        """
        Validate function documentation.
        
        Args:
            function_doc: The function documentation to validate.
            
        Returns:
            List of validation error messages.
        """
        pass
```

## Template Engine Integration

### DocRenderer

Renderer for documentation.

```python
class DocRenderer:
    def __init__(self, engine: Optional[TemplateEngine] = None) -> None:
        """
        Initialize the documentation renderer.
        
        Args:
            engine: The template engine to use for rendering. If None, uses the default engine.
        """
        pass
    
    def render_markdown(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to Markdown documentation.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered Markdown documentation.
        """
        pass
    
    def render_rst(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to reStructuredText documentation.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered reStructuredText documentation.
        """
        pass
    
    def render_html_doc(self, template_name: str, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a template to HTML documentation.
        
        Args:
            template_name: Name of the template to render.
            context: Context to use for rendering the template.
            
        Returns:
            Rendered HTML documentation.
        """
        pass
    
    def render_readme(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a README.md file.
        
        Args:
            context: Context to use for rendering the README.
            
        Returns:
            Rendered README.md file.
        """
        pass
    
    def render_api_doc(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render API documentation.
        
        Args:
            context: Context to use for rendering the API documentation.
            
        Returns:
            Rendered API documentation.
        """
        pass
    
    def render_user_guide(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a user guide.
        
        Args:
            context: Context to use for rendering the user guide.
            
        Returns:
            Rendered user guide.
        """
        pass
    
    def render_developer_guide(self, context: Union[Dict[str, Any], TemplateContext]) -> str:
        """
        Render a developer guide.
        
        Args:
            context: Context to use for rendering the developer guide.
            
        Returns:
            Rendered developer guide.
        """
        pass
```
