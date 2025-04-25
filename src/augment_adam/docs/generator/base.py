"""
Base classes for documentation generators.

This module provides the base classes for documentation generators, which extract
documentation from code and generate documentation files.
"""

import os
import re
import ast
import inspect
import importlib
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type, get_type_hints

from augment_adam.utils.tagging import tag, TagCategory


@tag("docs.generator")
class DocGenerator(ABC):
    """
    Base class for documentation generators.
    
    This class defines the interface for documentation generators, which extract
    documentation from code and generate documentation files.
    
    Attributes:
        output_dir: The directory to output documentation files to.
        template: The template to use for generating documentation.
        metadata: Additional metadata for the generator.
    
    TODO(Issue #12): Add support for documentation versioning
    TODO(Issue #12): Implement documentation analytics
    """
    
    def __init__(
        self,
        output_dir: str,
        template: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the documentation generator.
        
        Args:
            output_dir: The directory to output documentation files to.
            template: The template to use for generating documentation.
            metadata: Additional metadata for the generator.
        """
        self.output_dir = output_dir
        self.template = template
        self.metadata = metadata or {}
    
    @abstractmethod
    def generate(self, source: Any) -> Dict[str, Any]:
        """
        Generate documentation from a source.
        
        Args:
            source: The source to generate documentation from.
            
        Returns:
            Dictionary of documentation data.
        """
        pass
    
    @abstractmethod
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
        # Generate documentation
        data = self.generate(source)
        
        # Save documentation
        self.save(data, output_file)
        
        return data
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the generator.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the generator.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)


@tag("docs.generator")
class ModuleDocGenerator(DocGenerator):
    """
    Generator for module documentation.
    
    This class generates documentation for Python modules, including module
    docstrings, classes, functions, and variables.
    
    Attributes:
        output_dir: The directory to output documentation files to.
        template: The template to use for generating documentation.
        metadata: Additional metadata for the generator.
        include_private: Whether to include private members in the documentation.
        include_dunder: Whether to include dunder methods in the documentation.
    
    TODO(Issue #12): Add support for module dependencies
    TODO(Issue #12): Implement module analytics
    """
    
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
        super().__init__(output_dir, template, metadata)
        self.include_private = include_private
        self.include_dunder = include_dunder
    
    def generate(self, source: Union[str, Any]) -> Dict[str, Any]:
        """
        Generate documentation for a module.
        
        Args:
            source: The module to generate documentation for, either as a module object or a module name.
            
        Returns:
            Dictionary of module documentation data.
        """
        # Get module object
        if isinstance(source, str):
            module = importlib.import_module(source)
        else:
            module = source
        
        # Get module name and docstring
        module_name = module.__name__
        module_doc = inspect.getdoc(module) or ""
        
        # Get module members
        classes = []
        functions = []
        variables = []
        
        for name, obj in inspect.getmembers(module):
            # Skip private members if not included
            if not self.include_private and name.startswith("_") and not (self.include_dunder and name.startswith("__") and name.endswith("__")):
                continue
            
            # Categorize member
            if inspect.isclass(obj) and obj.__module__ == module_name:
                classes.append(self._get_class_data(obj))
            elif inspect.isfunction(obj) and obj.__module__ == module_name:
                functions.append(self._get_function_data(obj))
            elif not inspect.ismodule(obj) and not inspect.isbuiltin(obj) and not name.startswith("__"):
                variables.append({
                    "name": name,
                    "value": str(obj),
                    "type": type(obj).__name__,
                })
        
        # Create module data
        module_data = {
            "name": module_name,
            "doc": module_doc,
            "classes": classes,
            "functions": functions,
            "variables": variables,
            "file": inspect.getfile(module),
        }
        
        return module_data
    
    def save(self, data: Dict[str, Any], output_file: str) -> None:
        """
        Save module documentation to a file.
        
        Args:
            data: The module documentation data to save.
            output_file: The file to save the documentation to.
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Render documentation using template
        if self.template is not None:
            content = self.template.render(data)
        else:
            # Default rendering
            content = self._default_render(data)
        
        # Write to file
        with open(output_file, "w") as f:
            f.write(content)
    
    def _get_class_data(self, cls: Type) -> Dict[str, Any]:
        """
        Get documentation data for a class.
        
        Args:
            cls: The class to get documentation data for.
            
        Returns:
            Dictionary of class documentation data.
        """
        # Get class name and docstring
        class_name = cls.__name__
        class_doc = inspect.getdoc(cls) or ""
        
        # Get class members
        methods = []
        attributes = []
        
        for name, obj in inspect.getmembers(cls):
            # Skip private members if not included
            if not self.include_private and name.startswith("_") and not (self.include_dunder and name.startswith("__") and name.endswith("__")):
                continue
            
            # Categorize member
            if inspect.isfunction(obj) or inspect.ismethod(obj):
                methods.append(self._get_function_data(obj))
            elif not inspect.isclass(obj) and not inspect.isfunction(obj) and not inspect.ismethod(obj) and not name.startswith("__"):
                attributes.append({
                    "name": name,
                    "value": str(obj),
                    "type": type(obj).__name__,
                })
        
        # Get base classes
        bases = [base.__name__ for base in cls.__bases__ if base.__name__ != "object"]
        
        # Create class data
        class_data = {
            "name": class_name,
            "doc": class_doc,
            "methods": methods,
            "attributes": attributes,
            "bases": bases,
        }
        
        return class_data
    
    def _get_function_data(self, func: Callable) -> Dict[str, Any]:
        """
        Get documentation data for a function.
        
        Args:
            func: The function to get documentation data for.
            
        Returns:
            Dictionary of function documentation data.
        """
        # Get function name and docstring
        func_name = func.__name__
        func_doc = inspect.getdoc(func) or ""
        
        # Get function signature
        try:
            signature = inspect.signature(func)
            parameters = []
            
            for name, param in signature.parameters.items():
                # Get parameter type hint
                type_hint = ""
                try:
                    type_hints = get_type_hints(func)
                    if name in type_hints:
                        type_hint = str(type_hints[name])
                except Exception:
                    pass
                
                parameters.append({
                    "name": name,
                    "default": str(param.default) if param.default is not inspect.Parameter.empty else None,
                    "kind": str(param.kind),
                    "type": type_hint,
                })
            
            # Get return type hint
            return_type = ""
            try:
                type_hints = get_type_hints(func)
                if "return" in type_hints:
                    return_type = str(type_hints["return"])
            except Exception:
                pass
            
            # Create function data
            func_data = {
                "name": func_name,
                "doc": func_doc,
                "parameters": parameters,
                "return_type": return_type,
            }
            
            return func_data
        except Exception as e:
            # If signature cannot be determined, return basic data
            return {
                "name": func_name,
                "doc": func_doc,
                "parameters": [],
                "return_type": "",
                "error": str(e),
            }
    
    def _default_render(self, data: Dict[str, Any]) -> str:
        """
        Default rendering for module documentation.
        
        Args:
            data: The module documentation data to render.
            
        Returns:
            Rendered documentation as a string.
        """
        lines = []
        
        # Module header
        lines.append(f"# {data['name']}")
        lines.append("")
        
        # Module docstring
        if data["doc"]:
            lines.append(data["doc"])
            lines.append("")
        
        # Classes
        if data["classes"]:
            lines.append("## Classes")
            lines.append("")
            
            for cls in data["classes"]:
                lines.append(f"### {cls['name']}")
                lines.append("")
                
                if cls["bases"]:
                    lines.append(f"Bases: {', '.join(cls['bases'])}")
                    lines.append("")
                
                if cls["doc"]:
                    lines.append(cls["doc"])
                    lines.append("")
                
                if cls["attributes"]:
                    lines.append("#### Attributes")
                    lines.append("")
                    
                    for attr in cls["attributes"]:
                        lines.append(f"- `{attr['name']}` ({attr['type']}): {attr['value']}")
                    
                    lines.append("")
                
                if cls["methods"]:
                    lines.append("#### Methods")
                    lines.append("")
                    
                    for method in cls["methods"]:
                        params = ", ".join([f"{p['name']}: {p['type']}" if p['type'] else p['name'] for p in method["parameters"]])
                        lines.append(f"- `{method['name']}({params})` -> {method['return_type']}")
                        
                        if method["doc"]:
                            lines.append(f"  {method['doc'].split(chr(10))[0]}")
                    
                    lines.append("")
        
        # Functions
        if data["functions"]:
            lines.append("## Functions")
            lines.append("")
            
            for func in data["functions"]:
                params = ", ".join([f"{p['name']}: {p['type']}" if p['type'] else p['name'] for p in func["parameters"]])
                lines.append(f"### `{func['name']}({params})` -> {func['return_type']}")
                lines.append("")
                
                if func["doc"]:
                    lines.append(func["doc"])
                    lines.append("")
        
        # Variables
        if data["variables"]:
            lines.append("## Variables")
            lines.append("")
            
            for var in data["variables"]:
                lines.append(f"- `{var['name']}` ({var['type']}): {var['value']}")
            
            lines.append("")
        
        return "\n".join(lines)


@tag("docs.generator")
class ClassDocGenerator(DocGenerator):
    """
    Generator for class documentation.
    
    This class generates documentation for Python classes, including class
    docstrings, methods, and attributes.
    
    Attributes:
        output_dir: The directory to output documentation files to.
        template: The template to use for generating documentation.
        metadata: Additional metadata for the generator.
        include_private: Whether to include private members in the documentation.
        include_dunder: Whether to include dunder methods in the documentation.
    
    TODO(Issue #12): Add support for class inheritance
    TODO(Issue #12): Implement class analytics
    """
    
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
        super().__init__(output_dir, template, metadata)
        self.include_private = include_private
        self.include_dunder = include_dunder
    
    def generate(self, source: Type) -> Dict[str, Any]:
        """
        Generate documentation for a class.
        
        Args:
            source: The class to generate documentation for.
            
        Returns:
            Dictionary of class documentation data.
        """
        # Get class name and docstring
        class_name = source.__name__
        class_doc = inspect.getdoc(source) or ""
        
        # Get class members
        methods = []
        attributes = []
        
        for name, obj in inspect.getmembers(source):
            # Skip private members if not included
            if not self.include_private and name.startswith("_") and not (self.include_dunder and name.startswith("__") and name.endswith("__")):
                continue
            
            # Categorize member
            if inspect.isfunction(obj) or inspect.ismethod(obj):
                methods.append(self._get_function_data(obj))
            elif not inspect.isclass(obj) and not inspect.isfunction(obj) and not inspect.ismethod(obj) and not name.startswith("__"):
                attributes.append({
                    "name": name,
                    "value": str(obj),
                    "type": type(obj).__name__,
                })
        
        # Get base classes
        bases = [base.__name__ for base in source.__bases__ if base.__name__ != "object"]
        
        # Create class data
        class_data = {
            "name": class_name,
            "doc": class_doc,
            "methods": methods,
            "attributes": attributes,
            "bases": bases,
            "module": source.__module__,
        }
        
        return class_data
    
    def save(self, data: Dict[str, Any], output_file: str) -> None:
        """
        Save class documentation to a file.
        
        Args:
            data: The class documentation data to save.
            output_file: The file to save the documentation to.
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Render documentation using template
        if self.template is not None:
            content = self.template.render(data)
        else:
            # Default rendering
            content = self._default_render(data)
        
        # Write to file
        with open(output_file, "w") as f:
            f.write(content)
    
    def _get_function_data(self, func: Callable) -> Dict[str, Any]:
        """
        Get documentation data for a function.
        
        Args:
            func: The function to get documentation data for.
            
        Returns:
            Dictionary of function documentation data.
        """
        # Get function name and docstring
        func_name = func.__name__
        func_doc = inspect.getdoc(func) or ""
        
        # Get function signature
        try:
            signature = inspect.signature(func)
            parameters = []
            
            for name, param in signature.parameters.items():
                # Get parameter type hint
                type_hint = ""
                try:
                    type_hints = get_type_hints(func)
                    if name in type_hints:
                        type_hint = str(type_hints[name])
                except Exception:
                    pass
                
                parameters.append({
                    "name": name,
                    "default": str(param.default) if param.default is not inspect.Parameter.empty else None,
                    "kind": str(param.kind),
                    "type": type_hint,
                })
            
            # Get return type hint
            return_type = ""
            try:
                type_hints = get_type_hints(func)
                if "return" in type_hints:
                    return_type = str(type_hints["return"])
            except Exception:
                pass
            
            # Create function data
            func_data = {
                "name": func_name,
                "doc": func_doc,
                "parameters": parameters,
                "return_type": return_type,
            }
            
            return func_data
        except Exception as e:
            # If signature cannot be determined, return basic data
            return {
                "name": func_name,
                "doc": func_doc,
                "parameters": [],
                "return_type": "",
                "error": str(e),
            }
    
    def _default_render(self, data: Dict[str, Any]) -> str:
        """
        Default rendering for class documentation.
        
        Args:
            data: The class documentation data to render.
            
        Returns:
            Rendered documentation as a string.
        """
        lines = []
        
        # Class header
        lines.append(f"# {data['name']}")
        lines.append("")
        
        # Module
        lines.append(f"Module: `{data['module']}`")
        lines.append("")
        
        # Base classes
        if data["bases"]:
            lines.append(f"Bases: {', '.join(data['bases'])}")
            lines.append("")
        
        # Class docstring
        if data["doc"]:
            lines.append(data["doc"])
            lines.append("")
        
        # Attributes
        if data["attributes"]:
            lines.append("## Attributes")
            lines.append("")
            
            for attr in data["attributes"]:
                lines.append(f"- `{attr['name']}` ({attr['type']}): {attr['value']}")
            
            lines.append("")
        
        # Methods
        if data["methods"]:
            lines.append("## Methods")
            lines.append("")
            
            for method in data["methods"]:
                params = ", ".join([f"{p['name']}: {p['type']}" if p['type'] else p['name'] for p in method["parameters"]])
                lines.append(f"### `{method['name']}({params})` -> {method['return_type']}")
                lines.append("")
                
                if method["doc"]:
                    lines.append(method["doc"])
                    lines.append("")
        
        return "\n".join(lines)


@tag("docs.generator")
class FunctionDocGenerator(DocGenerator):
    """
    Generator for function documentation.
    
    This class generates documentation for Python functions, including function
    docstrings, parameters, and return types.
    
    Attributes:
        output_dir: The directory to output documentation files to.
        template: The template to use for generating documentation.
        metadata: Additional metadata for the generator.
    
    TODO(Issue #12): Add support for function annotations
    TODO(Issue #12): Implement function analytics
    """
    
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
        super().__init__(output_dir, template, metadata)
    
    def generate(self, source: Callable) -> Dict[str, Any]:
        """
        Generate documentation for a function.
        
        Args:
            source: The function to generate documentation for.
            
        Returns:
            Dictionary of function documentation data.
        """
        # Get function name and docstring
        func_name = source.__name__
        func_doc = inspect.getdoc(source) or ""
        
        # Get function signature
        try:
            signature = inspect.signature(source)
            parameters = []
            
            for name, param in signature.parameters.items():
                # Get parameter type hint
                type_hint = ""
                try:
                    type_hints = get_type_hints(source)
                    if name in type_hints:
                        type_hint = str(type_hints[name])
                except Exception:
                    pass
                
                parameters.append({
                    "name": name,
                    "default": str(param.default) if param.default is not inspect.Parameter.empty else None,
                    "kind": str(param.kind),
                    "type": type_hint,
                })
            
            # Get return type hint
            return_type = ""
            try:
                type_hints = get_type_hints(source)
                if "return" in type_hints:
                    return_type = str(type_hints["return"])
            except Exception:
                pass
            
            # Create function data
            func_data = {
                "name": func_name,
                "doc": func_doc,
                "parameters": parameters,
                "return_type": return_type,
                "module": source.__module__,
            }
            
            return func_data
        except Exception as e:
            # If signature cannot be determined, return basic data
            return {
                "name": func_name,
                "doc": func_doc,
                "parameters": [],
                "return_type": "",
                "module": source.__module__,
                "error": str(e),
            }
    
    def save(self, data: Dict[str, Any], output_file: str) -> None:
        """
        Save function documentation to a file.
        
        Args:
            data: The function documentation data to save.
            output_file: The file to save the documentation to.
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Render documentation using template
        if self.template is not None:
            content = self.template.render(data)
        else:
            # Default rendering
            content = self._default_render(data)
        
        # Write to file
        with open(output_file, "w") as f:
            f.write(content)
    
    def _default_render(self, data: Dict[str, Any]) -> str:
        """
        Default rendering for function documentation.
        
        Args:
            data: The function documentation data to render.
            
        Returns:
            Rendered documentation as a string.
        """
        lines = []
        
        # Function header
        params = ", ".join([f"{p['name']}: {p['type']}" if p['type'] else p['name'] for p in data["parameters"]])
        lines.append(f"# `{data['name']}({params})` -> {data['return_type']}")
        lines.append("")
        
        # Module
        lines.append(f"Module: `{data['module']}`")
        lines.append("")
        
        # Function docstring
        if data["doc"]:
            lines.append(data["doc"])
            lines.append("")
        
        # Parameters
        if data["parameters"]:
            lines.append("## Parameters")
            lines.append("")
            
            for param in data["parameters"]:
                type_str = f" ({param['type']})" if param['type'] else ""
                default_str = f" = {param['default']}" if param['default'] is not None else ""
                lines.append(f"- `{param['name']}{type_str}{default_str}`")
            
            lines.append("")
        
        # Return type
        if data["return_type"]:
            lines.append("## Returns")
            lines.append("")
            lines.append(f"- `{data['return_type']}`")
            lines.append("")
        
        return "\n".join(lines)
