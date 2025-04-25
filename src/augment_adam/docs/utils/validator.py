"""
Documentation validator.

This module provides a validator for validating documentation.
"""

import re
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type

from augment_adam.utils.tagging import tag, TagCategory


@tag("docs.utils")
class DocValidator:
    """
    Validator for documentation.
    
    This class validates documentation, ensuring it meets certain requirements
    and standards.
    
    Attributes:
        metadata: Additional metadata for the validator.
    
    TODO(Issue #12): Add support for more validation rules
    TODO(Issue #12): Implement validator analytics
    """
    
    def __init__(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the documentation validator.
        
        Args:
            metadata: Additional metadata for the validator.
        """
        self.metadata = metadata or {}
    
    def validate_docstring(self, docstring: str) -> List[str]:
        """
        Validate a docstring.
        
        Args:
            docstring: The docstring to validate.
            
        Returns:
            List of validation error messages.
        """
        errors = []
        
        # Check if docstring is empty
        if not docstring:
            errors.append("Docstring is empty")
            return errors
        
        # Check if docstring starts with a capital letter
        if not docstring[0].isupper():
            errors.append("Docstring should start with a capital letter")
        
        # Check if docstring ends with a period
        if not docstring.rstrip().endswith("."):
            errors.append("Docstring should end with a period")
        
        # Check if docstring has a description
        if len(docstring.split("\n\n")) < 1:
            errors.append("Docstring should have a description")
        
        return errors
    
    def validate_module_doc(self, module_doc: Dict[str, Any]) -> List[str]:
        """
        Validate module documentation.
        
        Args:
            module_doc: The module documentation to validate.
            
        Returns:
            List of validation error messages.
        """
        errors = []
        
        # Check if module name is present
        if "name" not in module_doc:
            errors.append("Module name is missing")
        
        # Check if module docstring is present
        if "doc" not in module_doc:
            errors.append("Module docstring is missing")
        elif not module_doc["doc"]:
            errors.append("Module docstring is empty")
        
        # Validate module docstring
        if "doc" in module_doc and module_doc["doc"]:
            errors.extend(self.validate_docstring(module_doc["doc"]))
        
        return errors
    
    def validate_class_doc(self, class_doc: Dict[str, Any]) -> List[str]:
        """
        Validate class documentation.
        
        Args:
            class_doc: The class documentation to validate.
            
        Returns:
            List of validation error messages.
        """
        errors = []
        
        # Check if class name is present
        if "name" not in class_doc:
            errors.append("Class name is missing")
        
        # Check if class docstring is present
        if "doc" not in class_doc:
            errors.append("Class docstring is missing")
        elif not class_doc["doc"]:
            errors.append("Class docstring is empty")
        
        # Validate class docstring
        if "doc" in class_doc and class_doc["doc"]:
            errors.extend(self.validate_docstring(class_doc["doc"]))
        
        # Validate methods
        if "methods" in class_doc:
            for method in class_doc["methods"]:
                errors.extend(self.validate_function_doc(method))
        
        return errors
    
    def validate_function_doc(self, function_doc: Dict[str, Any]) -> List[str]:
        """
        Validate function documentation.
        
        Args:
            function_doc: The function documentation to validate.
            
        Returns:
            List of validation error messages.
        """
        errors = []
        
        # Check if function name is present
        if "name" not in function_doc:
            errors.append("Function name is missing")
        
        # Check if function docstring is present
        if "doc" not in function_doc:
            errors.append("Function docstring is missing")
        elif not function_doc["doc"]:
            errors.append("Function docstring is empty")
        
        # Validate function docstring
        if "doc" in function_doc and function_doc["doc"]:
            errors.extend(self.validate_docstring(function_doc["doc"]))
        
        # Check if parameters are documented
        if "parameters" in function_doc and function_doc["parameters"]:
            # Get parameter names from docstring
            param_pattern = r"Args:\s*\n((?:\s+\w+:.*\n)+)"
            if "doc" in function_doc and function_doc["doc"]:
                match = re.search(param_pattern, function_doc["doc"])
                if match:
                    param_text = match.group(1)
                    param_names = [line.strip().split(":")[0].strip() for line in param_text.split("\n") if line.strip()]
                    
                    # Check if all parameters are documented
                    for param in function_doc["parameters"]:
                        if "name" in param and param["name"] not in param_names and param["name"] != "self" and param["name"] != "cls":
                            errors.append(f"Parameter '{param['name']}' is not documented")
        
        return errors
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the validator.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the validator.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
