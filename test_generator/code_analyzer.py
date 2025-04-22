"""
Code analyzer module for extracting information from source code.
"""

import os
import ast
import libcst as cst
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from radon.complexity import cc_visit

@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    args: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    complexity: int
    source_code: str
    line_start: int
    line_end: int

@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    methods: List[FunctionInfo]
    docstring: Optional[str]
    source_code: str
    line_start: int
    line_end: int

@dataclass
class CodeInfo:
    """Information about the code."""
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    file_path: str = ""
    source_code: str = ""
    related_files: Dict[str, str] = field(default_factory=dict)

class CodeAnalyzer:
    """Analyzes source code to extract information."""
    
    def __init__(self, file_path: str, include_files: List[str] = None):
        """Initialize the code analyzer.
        
        Args:
            file_path: Path to the source file.
            include_files: Additional files to include for context.
        """
        self.file_path = file_path
        self.include_files = include_files or []
    
    def analyze(self) -> CodeInfo:
        """Analyze the source code.
        
        Returns:
            Information about the code.
        """
        code_info = CodeInfo(file_path=self.file_path)
        
        # Read the source file
        with open(self.file_path, "r") as f:
            source_code = f.read()
        
        code_info.source_code = source_code
        
        # Parse the source code
        tree = ast.parse(source_code)
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    code_info.imports.append(f"import {name.name}")
            elif isinstance(node, ast.ImportFrom):
                names = ", ".join(name.name for name in node.names)
                code_info.imports.append(f"from {node.module} import {names}")
        
        # Extract functions and classes
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                code_info.functions.append(self._extract_function_info(node, source_code))
            elif isinstance(node, ast.ClassDef):
                code_info.classes.append(self._extract_class_info(node, source_code))
        
        # Include related files
        for file_path in self.include_files:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    code_info.related_files[file_path] = f.read()
        
        return code_info
    
    def _extract_function_info(self, node: ast.FunctionDef, source_code: str) -> FunctionInfo:
        """Extract information about a function.
        
        Args:
            node: The AST node for the function.
            source_code: The source code.
            
        Returns:
            Information about the function.
        """
        # Extract arguments
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract return type
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns)
        
        # Extract source code
        line_start = node.lineno
        line_end = node.end_lineno
        function_source = "\n".join(source_code.split("\n")[line_start-1:line_end])
        
        # Calculate complexity
        complexity = 1  # Default complexity
        for item in cc_visit(function_source):
            if item.name == node.name:
                complexity = item.complexity
                break
        
        return FunctionInfo(
            name=node.name,
            args=args,
            returns=returns,
            docstring=docstring,
            complexity=complexity,
            source_code=function_source,
            line_start=line_start,
            line_end=line_end,
        )
    
    def _extract_class_info(self, node: ast.ClassDef, source_code: str) -> ClassInfo:
        """Extract information about a class.
        
        Args:
            node: The AST node for the class.
            source_code: The source code.
            
        Returns:
            Information about the class.
        """
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._extract_function_info(item, source_code))
        
        # Extract source code
        line_start = node.lineno
        line_end = node.end_lineno
        class_source = "\n".join(source_code.split("\n")[line_start-1:line_end])
        
        return ClassInfo(
            name=node.name,
            methods=methods,
            docstring=docstring,
            source_code=class_source,
            line_start=line_start,
            line_end=line_end,
        )
