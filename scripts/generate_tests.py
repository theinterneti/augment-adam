#!/usr/bin/env python3
"""
Test Generator.

This script generates test files for Python modules based on the code quality
checklist and the module's functionality.
"""

import argparse
import ast
import importlib
import inspect
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import augment_adam
except ImportError:
    print("Warning: Could not import augment_adam. Some checks may not work.")


class TestGenerator:
    """
    Generates test files for Python modules.
    """

    def __init__(self, file_path: str):
        """
        Initialize the generator with a file path.

        Args:
            file_path: Path to the Python file to generate tests for
        """
        self.file_path = file_path
        self.file_content = ""
        self.ast_tree = None
        self.module_name = ""
        self.class_info = []
        self.function_info = []
        
        # Load the file content
        self._load_file()
        
    def _load_file(self) -> None:
        """Load the file content and parse the AST."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.file_content = f.read()
            
            self.ast_tree = ast.parse(self.file_content)
            
            # Extract the module name from the file path
            file_name = os.path.basename(self.file_path)
            self.module_name = os.path.splitext(file_name)[0]
            
            # Extract information about classes and functions
            self._extract_class_info()
            self._extract_function_info()
            
        except Exception as e:
            print(f"Error loading file: {e}")
            sys.exit(1)
    
    def _extract_class_info(self) -> None:
        """Extract information about classes in the module."""
        if not self.ast_tree:
            return
            
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        methods.append({
                            'name': child.name,
                            'args': [arg.arg for arg in child.args.args if arg.arg != 'self'],
                            'docstring': ast.get_docstring(child) or "",
                            'is_async': isinstance(child, ast.AsyncFunctionDef),
                        })
                
                self.class_info.append({
                    'name': node.name,
                    'docstring': ast.get_docstring(node) or "",
                    'methods': methods,
                })
    
    def _extract_function_info(self) -> None:
        """Extract information about functions in the module."""
        if not self.ast_tree:
            return
            
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef) and node.parent_field == 'body':
                self.function_info.append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args if arg.arg not in ('self', 'cls')],
                    'docstring': ast.get_docstring(node) or "",
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                })
    
    def generate_unit_test(self) -> str:
        """
        Generate a unit test file for the module.
        
        Returns:
            The content of the unit test file
        """
        # Determine the import path
        relative_path = os.path.relpath(self.file_path, Path(__file__).parent.parent)
        import_path = os.path.splitext(relative_path)[0].replace(os.path.sep, '.')
        
        if import_path.startswith('src.'):
            import_path = import_path[4:]  # Remove 'src.' prefix
        
        # Generate the test file content
        content = [
            '"""',
            f'Unit tests for {import_path}.',
            '"""',
            '',
            'import unittest',
            'import pytest',
            'from unittest.mock import MagicMock, patch',
            '',
            f'from {import_path} import *',
            '',
            '',
        ]
        
        # Add test classes for each class in the module
        for cls_info in self.class_info:
            content.extend([
                f'class Test{cls_info["name"]}(unittest.TestCase):',
                f'    """Test cases for the {cls_info["name"]} class."""',
                '',
                '    def setUp(self):',
                '        """Set up the test case."""',
                '        # TODO: Set up test fixtures',
                '        pass',
                '',
                '    def tearDown(self):',
                '        """Tear down the test case."""',
                '        # TODO: Clean up test fixtures',
                '        pass',
                '',
            ])
            
            # Add test methods for each method in the class
            for method_info in cls_info['methods']:
                # Skip special methods
                if method_info['name'].startswith('__') and method_info['name'].endswith('__'):
                    continue
                    
                content.extend([
                    f'    def test_{method_info["name"]}(self):',
                    f'        """Test {method_info["name"]} method."""',
                    '        # TODO: Implement test',
                    f'        # instance = {cls_info["name"]}()',
                    f'        # result = instance.{method_info["name"]}()',
                    '        # self.assertEqual(expected, result)',
                    '        pass',
                    '',
                ])
            
            content.append('')
        
        # Add test functions for each function in the module
        if self.function_info:
            content.extend([
                'class TestFunctions(unittest.TestCase):',
                '    """Test cases for module-level functions."""',
                '',
            ])
            
            for func_info in self.function_info:
                # Skip special functions
                if func_info['name'].startswith('__') and func_info['name'].endswith('__'):
                    continue
                    
                content.extend([
                    f'    def test_{func_info["name"]}(self):',
                    f'        """Test {func_info["name"]} function."""',
                    '        # TODO: Implement test',
                    f'        # result = {func_info["name"]}()',
                    '        # self.assertEqual(expected, result)',
                    '        pass',
                    '',
                ])
            
            content.append('')
        
        # Add main block
        content.extend([
            "if __name__ == '__main__':",
            '    unittest.main()',
            '',
        ])
        
        return '\n'.join(content)
    
    def generate_integration_test(self) -> str:
        """
        Generate an integration test file for the module.
        
        Returns:
            The content of the integration test file
        """
        # Determine the import path
        relative_path = os.path.relpath(self.file_path, Path(__file__).parent.parent)
        import_path = os.path.splitext(relative_path)[0].replace(os.path.sep, '.')
        
        if import_path.startswith('src.'):
            import_path = import_path[4:]  # Remove 'src.' prefix
        
        # Generate the test file content
        content = [
            '"""',
            f'Integration tests for {import_path}.',
            '"""',
            '',
            'import unittest',
            'import pytest',
            'from unittest.mock import MagicMock, patch',
            '',
            f'from {import_path} import *',
            '',
            '',
            '@pytest.mark.integration',
            f'class Test{self.module_name.capitalize()}Integration(unittest.TestCase):',
            f'    """Integration tests for {self.module_name}."""',
            '',
            '    def setUp(self):',
            '        """Set up the test case."""',
            '        # TODO: Set up test fixtures',
            '        pass',
            '',
            '    def tearDown(self):',
            '        """Tear down the test case."""',
            '        # TODO: Clean up test fixtures',
            '        pass',
            '',
            '    def test_integration(self):',
            f'        """Test {self.module_name} integration."""',
            '        # TODO: Implement integration test',
            '        pass',
            '',
            '',
            "if __name__ == '__main__':",
            '    unittest.main()',
            '',
        ]
        
        return '\n'.join(content)
    
    def generate_e2e_test(self) -> str:
        """
        Generate an end-to-end test file for the module.
        
        Returns:
            The content of the end-to-end test file
        """
        # Determine the import path
        relative_path = os.path.relpath(self.file_path, Path(__file__).parent.parent)
        import_path = os.path.splitext(relative_path)[0].replace(os.path.sep, '.')
        
        if import_path.startswith('src.'):
            import_path = import_path[4:]  # Remove 'src.' prefix
        
        # Generate the test file content
        content = [
            '"""',
            f'End-to-end tests for {import_path}.',
            '"""',
            '',
            'import unittest',
            'import pytest',
            'from unittest.mock import MagicMock, patch',
            '',
            f'from {import_path} import *',
            '',
            '',
            '@pytest.mark.e2e',
            f'class Test{self.module_name.capitalize()}E2E(unittest.TestCase):',
            f'    """End-to-end tests for {self.module_name}."""',
            '',
            '    def setUp(self):',
            '        """Set up the test case."""',
            '        # TODO: Set up test fixtures',
            '        pass',
            '',
            '    def tearDown(self):',
            '        """Tear down the test case."""',
            '        # TODO: Clean up test fixtures',
            '        pass',
            '',
            '    def test_e2e(self):',
            f'        """Test {self.module_name} end-to-end."""',
            '        # TODO: Implement end-to-end test',
            '        pass',
            '',
            '',
            "if __name__ == '__main__':",
            '    unittest.main()',
            '',
        ]
        
        return '\n'.join(content)
    
    def save_test_files(self, output_dir: str) -> List[str]:
        """
        Save the generated test files to the output directory.
        
        Args:
            output_dir: Directory to save the test files
            
        Returns:
            List of paths to the saved test files
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = []
        
        # Save the unit test file
        unit_test_path = os.path.join(output_dir, f'test_{self.module_name}.py')
        with open(unit_test_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_unit_test())
        saved_files.append(unit_test_path)
        
        # Save the integration test file
        integration_test_path = os.path.join(output_dir, f'test_{self.module_name}_integration.py')
        with open(integration_test_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_integration_test())
        saved_files.append(integration_test_path)
        
        # Save the end-to-end test file
        e2e_test_path = os.path.join(output_dir, f'test_{self.module_name}_e2e.py')
        with open(e2e_test_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_e2e_test())
        saved_files.append(e2e_test_path)
        
        return saved_files


def main():
    """Run the test generator on a file."""
    parser = argparse.ArgumentParser(description="Generate tests for a Python file")
    parser.add_argument("--file", required=True, help="Path to the Python file to generate tests for")
    parser.add_argument("--output-dir", default="tests", help="Directory to save the test files (default: tests)")
    parser.add_argument("--unit-only", action="store_true", help="Generate only unit tests")
    parser.add_argument("--integration-only", action="store_true", help="Generate only integration tests")
    parser.add_argument("--e2e-only", action="store_true", help="Generate only end-to-end tests")
    args = parser.parse_args()
    
    generator = TestGenerator(args.file)
    
    if args.unit_only:
        unit_test_content = generator.generate_unit_test()
        unit_test_path = os.path.join(args.output_dir, f'test_{generator.module_name}.py')
        os.makedirs(os.path.dirname(unit_test_path), exist_ok=True)
        with open(unit_test_path, 'w', encoding='utf-8') as f:
            f.write(unit_test_content)
        print(f"Unit test file saved to {unit_test_path}")
    elif args.integration_only:
        integration_test_content = generator.generate_integration_test()
        integration_test_path = os.path.join(args.output_dir, f'test_{generator.module_name}_integration.py')
        os.makedirs(os.path.dirname(integration_test_path), exist_ok=True)
        with open(integration_test_path, 'w', encoding='utf-8') as f:
            f.write(integration_test_content)
        print(f"Integration test file saved to {integration_test_path}")
    elif args.e2e_only:
        e2e_test_content = generator.generate_e2e_test()
        e2e_test_path = os.path.join(args.output_dir, f'test_{generator.module_name}_e2e.py')
        os.makedirs(os.path.dirname(e2e_test_path), exist_ok=True)
        with open(e2e_test_path, 'w', encoding='utf-8') as f:
            f.write(e2e_test_content)
        print(f"End-to-end test file saved to {e2e_test_path}")
    else:
        saved_files = generator.save_test_files(args.output_dir)
        print(f"Test files saved to:")
        for file_path in saved_files:
            print(f"  {file_path}")


if __name__ == "__main__":
    main()
