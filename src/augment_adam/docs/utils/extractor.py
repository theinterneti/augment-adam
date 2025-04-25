"""
Documentation extractor.

This module provides an extractor for extracting documentation from code.
"""

import os
import re
import ast
import inspect
import importlib
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type, get_type_hints

from augment_adam.utils.tagging import tag, TagCategory


@tag("docs.utils")
class DocExtractor:
    """
    Extractor for documentation.
    
    This class extracts documentation from code, including docstrings, type hints,
    and other metadata.
    
    Attributes:
        metadata: Additional metadata for the extractor.
    
    TODO(Issue #12): Add support for more documentation sources
    TODO(Issue #12): Implement extractor validation
    """
    
    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the documentation extractor.
        
        Args:
            metadata: Additional metadata for the extractor.
        """
        self.metadata = metadata or {}
    
    def extract_module(self, module: Union[str, Any]) -> Dict[str, Any]:
        """
        Extract documentation from a module.
        
        Args:
            module: The module to extract documentation from, either as a module object or a module name.
            
        Returns:
            Dictionary of module documentation data.
        """
        # Get module object
        if isinstance(module, str):
            module = importlib.import_module(module)
        
        # Get module name and docstring
        module_name = module.__name__
        module_doc = inspect.getdoc(module) or ""
        
        # Get module members
        classes = []
        functions = []
        variables = []
        
        for name, obj in inspect.getmembers(module):
            # Skip private members
            if name.startswith("_"):
                continue
            
            # Categorize member
            if inspect.isclass(obj) and obj.__module__ == module_name:
                classes.append(self.extract_class(obj))
            elif inspect.isfunction(obj) and obj.__module__ == module_name:
                functions.append(self.extract_function(obj))
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
    
    def extract_class(self, cls: Type) -> Dict[str, Any]:
        """
        Extract documentation from a class.
        
        Args:
            cls: The class to extract documentation from.
            
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
            # Skip private members
            if name.startswith("_") and name != "__init__":
                continue
            
            # Categorize member
            if inspect.isfunction(obj) or inspect.ismethod(obj):
                methods.append(self.extract_function(obj))
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
            "module": cls.__module__,
        }
        
        return class_data
    
    def extract_function(self, func: Callable) -> Dict[str, Any]:
        """
        Extract documentation from a function.
        
        Args:
            func: The function to extract documentation from.
            
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
                "module": func.__module__,
            }
            
            return func_data
        except Exception as e:
            # If signature cannot be determined, return basic data
            return {
                "name": func_name,
                "doc": func_doc,
                "parameters": [],
                "return_type": "",
                "module": func.__module__,
                "error": str(e),
            }
    
    def extract_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract documentation from a Python file.
        
        Args:
            file_path: The path to the Python file.
            
        Returns:
            Dictionary of file documentation data.
        """
        # Read file
        with open(file_path, "r") as f:
            source = f.read()
        
        # Parse AST
        tree = ast.parse(source)
        
        # Get module docstring
        module_doc = ast.get_docstring(tree) or ""
        
        # Get classes and functions
        classes = []
        functions = []
        variables = []
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                # Extract class documentation
                class_doc = ast.get_docstring(node) or ""
                
                # Get methods
                methods = []
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Extract method documentation
                        method_doc = ast.get_docstring(item) or ""
                        
                        methods.append({
                            "name": item.name,
                            "doc": method_doc,
                        })
                
                classes.append({
                    "name": node.name,
                    "doc": class_doc,
                    "methods": methods,
                })
            elif isinstance(node, ast.FunctionDef):
                # Extract function documentation
                func_doc = ast.get_docstring(node) or ""
                
                functions.append({
                    "name": node.name,
                    "doc": func_doc,
                })
            elif isinstance(node, ast.Assign):
                # Extract variable documentation
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append({
                            "name": target.id,
                        })
        
        # Create file data
        file_data = {
            "name": os.path.basename(file_path),
            "doc": module_doc,
            "classes": classes,
            "functions": functions,
            "variables": variables,
            "path": file_path,
        }
        
        return file_data
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the extractor.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the extractor.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
