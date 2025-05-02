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

        # Get top-level functions
        for node in self.ast_tree.body:
            if isinstance(node, ast.FunctionDef):
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
            '# Import test utilities',
            'from tests.utils import (',
            '    skip_if_no_module,',
            '    timed,',
            '    assert_dict_subset,',
            '    assert_lists_equal_unordered,',
            '    assert_approx_equal,',
            ')',
            '',
            '',
        ]

        # Add test classes for each class in the module
        for cls_info in self.class_info:
            content.extend([
                '@pytest.mark.unit',
                f'class Test{cls_info["name"]}(unittest.TestCase):',
                f'    """Test cases for the {cls_info["name"]} class."""',
                '',
                '    def setUp(self):',
                '        """Set up the test case."""',
                '        # Initialize objects for testing',
                f'        # self.obj = {cls_info["name"]}()',
                '        pass',
                '',
                '    def tearDown(self):',
                '        """Tear down the test case."""',
                '        # Clean up resources',
                '        pass',
                '',
            ])

            # Add test methods for each method in the class
            for method_info in cls_info['methods']:
                # Skip special methods
                if method_info['name'].startswith('__') and method_info['name'].endswith('__'):
                    continue

                # Generate method arguments
                args = method_info.get('args', [])
                arg_str = ', '.join([f'"{arg}"' for arg in args])

                # Generate docstring with more details
                docstring = method_info.get('docstring', '').strip()
                if docstring:
                    docstring_summary = docstring.split('.')[0] + '.'
                else:
                    docstring_summary = f"Test the {method_info['name']} method."

                # Generate test method
                content.extend([
                    f'    def test_{method_info["name"]}(self):',
                    f'        """{docstring_summary}"""',
                    '        # Arrange',
                    '        # expected = "expected result"',
                    '',
                    '        # Act',
                    f'        # result = self.obj.{method_info["name"]}({arg_str})',
                    '',
                    '        # Assert',
                    '        # self.assertEqual(expected, result)',
                    '        pass',
                    '',
                ])

                # Add a test for edge cases if there are arguments
                if args:
                    content.extend([
                        f'    def test_{method_info["name"]}_edge_cases(self):',
                        f'        """Test {method_info["name"]} method with edge cases."""',
                        '        # Test with edge cases',
                        '        # Edge case 1: Empty input',
                        f'        # result = self.obj.{method_info["name"]}("")',
                        '        # self.assertEqual(expected_empty, result)',
                        '',
                        '        # Edge case 2: None input',
                        f'        # with self.assertRaises(ValueError):',
                        f'        #     self.obj.{method_info["name"]}(None)',
                        '        pass',
                        '',
                    ])

                # Add a test with mocked dependencies if the method has arguments
                if args:
                    content.extend([
                        f'    @patch("{import_path}.dependency")',
                        f'    def test_{method_info["name"]}_with_mocks(self, mock_dependency):',
                        f'        """Test {method_info["name"]} method with mocked dependencies."""',
                        '        # Arrange',
                        '        # mock_dependency.return_value = "mocked result"',
                        '        # expected = "expected result"',
                        '',
                        '        # Act',
                        f'        # result = self.obj.{method_info["name"]}({arg_str})',
                        '',
                        '        # Assert',
                        '        # self.assertEqual(expected, result)',
                        '        # mock_dependency.assert_called_once_with({arg_str})',
                        '        pass',
                        '',
                    ])

            # Add a test for class initialization
            content.extend([
                '    def test_init(self):',
                f'        """Test {cls_info["name"]} initialization."""',
                '        # Test initialization with default parameters',
                f'        # obj = {cls_info["name"]}()',
                '        # self.assertIsInstance(obj, {cls_info["name"]})',
                '',
                '        # Test initialization with custom parameters',
                f'        # obj = {cls_info["name"]}(param1="value1", param2="value2")',
                '        # self.assertEqual("value1", obj.param1)',
                '        # self.assertEqual("value2", obj.param2)',
                '        pass',
                '',
            ])

            content.append('')

        # Add test functions for each function in the module
        if self.function_info:
            content.extend([
                '@pytest.mark.unit',
                'class TestFunctions(unittest.TestCase):',
                '    """Test cases for module-level functions."""',
                '',
            ])

            for func_info in self.function_info:
                # Skip special functions
                if func_info['name'].startswith('__') and func_info['name'].endswith('__'):
                    continue

                # Generate function arguments
                args = func_info.get('args', [])
                arg_str = ', '.join([f'"{arg}"' for arg in args])

                # Generate docstring with more details
                docstring = func_info.get('docstring', '').strip()
                if docstring:
                    docstring_summary = docstring.split('.')[0] + '.'
                else:
                    docstring_summary = f"Test the {func_info['name']} function."

                # Generate test method
                content.extend([
                    f'    def test_{func_info["name"]}(self):',
                    f'        """{docstring_summary}"""',
                    '        # Arrange',
                    '        # input_value = "input"',
                    '        # expected = "expected result"',
                    '',
                    '        # Act',
                    f'        # result = {func_info["name"]}({arg_str})',
                    '',
                    '        # Assert',
                    '        # self.assertEqual(expected, result)',
                    '        pass',
                    '',
                ])

                # Add a test for edge cases if there are arguments
                if args:
                    content.extend([
                        f'    def test_{func_info["name"]}_edge_cases(self):',
                        f'        """Test {func_info["name"]} function with edge cases."""',
                        '        # Test with edge cases',
                        '        # Edge case 1: Empty input',
                        f'        # result = {func_info["name"]}("")',
                        '        # self.assertEqual(expected_empty, result)',
                        '',
                        '        # Edge case 2: None input',
                        f'        # with self.assertRaises(ValueError):',
                        f'        #     {func_info["name"]}(None)',
                        '        pass',
                        '',
                    ])

                # Add a test with mocked dependencies if the function has arguments
                if args:
                    content.extend([
                        f'    @patch("{import_path}.dependency")',
                        f'    def test_{func_info["name"]}_with_mocks(self, mock_dependency):',
                        f'        """Test {func_info["name"]} function with mocked dependencies."""',
                        '        # Arrange',
                        '        # mock_dependency.return_value = "mocked result"',
                        '        # expected = "expected result"',
                        '',
                        '        # Act',
                        f'        # result = {func_info["name"]}({arg_str})',
                        '',
                        '        # Assert',
                        '        # self.assertEqual(expected, result)',
                        '        # mock_dependency.assert_called_once_with({arg_str})',
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
            'import os',
            'import tempfile',
            'from unittest.mock import MagicMock, patch',
            '',
            f'from {import_path} import *',
            '',
            '# Import test utilities',
            'from tests.utils import (',
            '    skip_if_no_module,',
            '    skip_if_no_env_var,',
            '    timed,',
            '    create_temp_file,',
            '    create_temp_dir,',
            '    AsyncTestCase,',
            ')',
            '',
            '',
            '@pytest.mark.integration',
            f'class Test{self.module_name.capitalize()}Integration(unittest.TestCase):',
            f'    """Integration tests for {self.module_name}."""',
            '',
            '    @classmethod',
            '    def setUpClass(cls):',
            '        """Set up the test class."""',
            '        # Initialize resources that are shared across all tests',
            '        pass',
            '',
            '    @classmethod',
            '    def tearDownClass(cls):',
            '        """Tear down the test class."""',
            '        # Clean up shared resources',
            '        pass',
            '',
            '    def setUp(self):',
            '        """Set up the test case."""',
            '        # Initialize objects for testing',
            '        # self.temp_dir = create_temp_dir()',
            '        # self.temp_file = create_temp_file("test content")',
            '        pass',
            '',
            '    def tearDown(self):',
            '        """Tear down the test case."""',
            '        # Clean up resources',
            '        # if self.temp_file.exists():',
            '        #     self.temp_file.unlink()',
            '        # if self.temp_dir.exists():',
            '        #     self.temp_dir.rmdir()',
            '        pass',
            '',
        ]

        # Add integration tests for each class in the module
        for cls_info in self.class_info:
            content.extend([
                f'    def test_{cls_info["name"].lower()}_integration(self):',
                f'        """Test integration with {cls_info["name"]}."""',
                f'        # Create an instance of {cls_info["name"]}',
                f'        # obj = {cls_info["name"]}()',
                '',
                '        # Perform integration test',
                '        # result = obj.method()',
                '',
                '        # Assert the result',
                '        # self.assertEqual(expected, result)',
                '        pass',
                '',
            ])

        # Add integration tests for functions in the module
        if self.function_info:
            content.extend([
                '    def test_function_integration(self):',
                '        """Test integration with module functions."""',
                '        # Test integration with module functions',
                '        # result = function()',
                '',
                '        # Assert the result',
                '        # self.assertEqual(expected, result)',
                '        pass',
                '',
            ])

        # Add a test for external dependencies
        content.extend([
            '    @skip_if_no_env_var("EXTERNAL_SERVICE_URL")',
            '    def test_external_integration(self):',
            '        """Test integration with external services."""',
            '        # This test will be skipped if EXTERNAL_SERVICE_URL is not set',
            '        # service_url = os.environ["EXTERNAL_SERVICE_URL"]',
            '',
            '        # Test integration with external service',
            '        # result = call_external_service(service_url)',
            '',
            '        # Assert the result',
            '        # self.assertEqual(expected, result)',
            '        pass',
            '',
        ])

        # Add a performance test
        content.extend([
            '    @timed',
            '    def test_performance_integration(self):',
            '        """Test performance in an integration scenario."""',
            '        # This test will print the time it took to run',
            '',
            '        # Perform a performance-critical operation',
            '        # result = performance_critical_operation()',
            '',
            '        # Assert the result',
            '        # self.assertEqual(expected, result)',
            '        pass',
            '',
        ])

        # Add an async test class if needed
        if any(method.get('is_async', False) for cls in self.class_info for method in cls['methods']):
            content.extend([
                '',
                '@pytest.mark.integration',
                f'class Test{self.module_name.capitalize()}AsyncIntegration(AsyncTestCase):',
                f'    """Async integration tests for {self.module_name}."""',
                '',
                '    async def asyncSetUp(self):',
                '        """Set up the async test case."""',
                '        # Initialize async objects for testing',
                '        pass',
                '',
                '    async def asyncTearDown(self):',
                '        """Tear down the async test case."""',
                '        # Clean up async resources',
                '        pass',
                '',
                '    def test_async_integration(self):',
                f'        """Test async integration with {self.module_name}."""',
                '',
                '        # Define the async test',
                '        async def async_test():',
                '            # Perform async integration test',
                '            # result = await async_operation()',
                '',
                '            # Assert the result',
                '            # self.assertEqual(expected, result)',
                '            pass',
                '',
                '        # Run the async test',
                '        self.run_async(async_test())',
                '',
            ])

        # Add main block
        content.extend([
            '',
            "if __name__ == '__main__':",
            '    unittest.main()',
            '',
        ])

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
            'import os',
            'import time',
            'import tempfile',
            'from unittest.mock import MagicMock, patch',
            '',
            f'from {import_path} import *',
            '',
            '# Import test utilities',
            'from tests.utils import (',
            '    skip_if_no_module,',
            '    skip_if_no_env_var,',
            '    timed,',
            '    create_temp_file,',
            '    create_temp_dir,',
            '    AsyncTestCase,',
            ')',
            '',
            '',
            '@pytest.mark.e2e',
            f'class Test{self.module_name.capitalize()}E2E(unittest.TestCase):',
            f'    """End-to-end tests for {self.module_name}."""',
            '',
            '    @classmethod',
            '    def setUpClass(cls):',
            '        """Set up the test class."""',
            '        # Initialize resources that are shared across all tests',
            '        # cls.server = Server()',
            '        # cls.server.start()',
            '        pass',
            '',
            '    @classmethod',
            '    def tearDownClass(cls):',
            '        """Tear down the test class."""',
            '        # Clean up shared resources',
            '        # cls.server.stop()',
            '        pass',
            '',
            '    def setUp(self):',
            '        """Set up the test case."""',
            '        # Initialize objects for testing',
            '        # self.client = Client()',
            '        # self.temp_dir = create_temp_dir()',
            '        pass',
            '',
            '    def tearDown(self):',
            '        """Tear down the test case."""',
            '        # Clean up resources',
            '        # self.client.close()',
            '        # if self.temp_dir.exists():',
            '        #     self.temp_dir.rmdir()',
            '        pass',
            '',
        ]

        # Add a basic end-to-end test
        content.extend([
            '    def test_basic_e2e(self):',
            f'        """Test basic end-to-end functionality of {self.module_name}."""',
            '        # Set up the test scenario',
            '        # input_data = {"key": "value"}',
            '        # expected_output = {"result": "success"}',
            '',
            '        # Execute the end-to-end flow',
            '        # result = self.client.process(input_data)',
            '',
            '        # Verify the result',
            '        # self.assertEqual(expected_output, result)',
            '        pass',
            '',
        ])

        # Add a complex end-to-end test
        content.extend([
            '    def test_complex_e2e(self):',
            f'        """Test complex end-to-end functionality of {self.module_name}."""',
            '        # Set up a complex test scenario',
            '        # input_data = [{"key1": "value1"}, {"key2": "value2"}]',
            '        # expected_output = [{"result1": "success"}, {"result2": "success"}]',
            '',
            '        # Execute the complex end-to-end flow',
            '        # results = []',
            '        # for item in input_data:',
            '        #     result = self.client.process(item)',
            '        #     results.append(result)',
            '',
            '        # Verify the results',
            '        # self.assertEqual(expected_output, results)',
            '        pass',
            '',
        ])

        # Add an error handling test
        content.extend([
            '    def test_error_handling_e2e(self):',
            f'        """Test error handling in end-to-end scenarios for {self.module_name}."""',
            '        # Set up an error scenario',
            '        # invalid_input = {"invalid": "data"}',
            '',
            '        # Verify that the system handles errors correctly',
            '        # with self.assertRaises(ValueError):',
            '        #     self.client.process(invalid_input)',
            '',
            '        # Verify that the system is still in a valid state after an error',
            '        # valid_input = {"key": "value"}',
            '        # result = self.client.process(valid_input)',
            '        # self.assertEqual({"result": "success"}, result)',
            '        pass',
            '',
        ])

        # Add a performance test
        content.extend([
            '    @timed',
            '    def test_performance_e2e(self):',
            f'        """Test performance in end-to-end scenarios for {self.module_name}."""',
            '        # This test will print the time it took to run',
            '',
            '        # Set up a performance test scenario',
            '        # large_input = {"data": "x" * 1000000}',
            '',
            '        # Execute the end-to-end flow with a large input',
            '        # start_time = time.time()',
            '        # result = self.client.process(large_input)',
            '        # end_time = time.time()',
            '',
            '        # Verify that the processing time is within acceptable limits',
            '        # self.assertLess(end_time - start_time, 1.0)  # Should complete in less than 1 second',
            '        pass',
            '',
        ])

        # Add a test that requires an environment variable
        content.extend([
            '    @skip_if_no_env_var("E2E_TEST_ENABLED")',
            '    def test_environment_dependent_e2e(self):',
            f'        """Test environment-dependent end-to-end functionality of {self.module_name}."""',
            '        # This test will be skipped if E2E_TEST_ENABLED is not set',
            '',
            '        # Set up the test scenario using environment variables',
            '        # config = {"api_key": os.environ.get("API_KEY")}',
            '        # client = Client(config)',
            '',
            '        # Execute the end-to-end flow',
            '        # result = client.process({"key": "value"})',
            '',
            '        # Verify the result',
            '        # self.assertEqual({"result": "success"}, result)',
            '        pass',
            '',
        ])

        # Add an async test class if needed
        if any(method.get('is_async', False) for cls in self.class_info for method in cls['methods']):
            content.extend([
                '',
                '@pytest.mark.e2e',
                f'class Test{self.module_name.capitalize()}AsyncE2E(AsyncTestCase):',
                f'    """Async end-to-end tests for {self.module_name}."""',
                '',
                '    @classmethod',
                '    async def asyncSetUpClass(cls):',
                '        """Set up the async test class."""',
                '        # Initialize async resources that are shared across all tests',
                '        # cls.server = await AsyncServer.create()',
                '        # await cls.server.start()',
                '        pass',
                '',
                '    @classmethod',
                '    async def asyncTearDownClass(cls):',
                '        """Tear down the async test class."""',
                '        # Clean up shared async resources',
                '        # await cls.server.stop()',
                '        pass',
                '',
                '    async def asyncSetUp(self):',
                '        """Set up the async test case."""',
                '        # Initialize async objects for testing',
                '        # self.client = await AsyncClient.create()',
                '        pass',
                '',
                '    async def asyncTearDown(self):',
                '        """Tear down the async test case."""',
                '        # Clean up async resources',
                '        # await self.client.close()',
                '        pass',
                '',
                '    def test_async_e2e(self):',
                f'        """Test async end-to-end functionality of {self.module_name}."""',
                '',
                '        # Define the async test',
                '        async def async_test():',
                '            # Set up the test scenario',
                '            # input_data = {"key": "value"}',
                '            # expected_output = {"result": "success"}',
                '',
                '            # Execute the async end-to-end flow',
                '            # result = await self.client.process(input_data)',
                '',
                '            # Verify the result',
                '            # self.assertEqual(expected_output, result)',
                '            pass',
                '',
                '        # Run the async test',
                '        self.run_async(async_test())',
                '',
            ])

        # Add a user journey test
        content.extend([
            '',
            '@pytest.mark.e2e',
            f'class Test{self.module_name.capitalize()}UserJourney(unittest.TestCase):',
            f'    """User journey tests for {self.module_name}."""',
            '',
            '    def setUp(self):',
            '        """Set up the test case."""',
            '        # Initialize objects for testing',
            '        # self.app = App()',
            '        pass',
            '',
            '    def tearDown(self):',
            '        """Tear down the test case."""',
            '        # Clean up resources',
            '        # self.app.close()',
            '        pass',
            '',
            '    def test_user_journey(self):',
            f'        """Test a complete user journey through {self.module_name}."""',
            '        # Set up the user journey',
            '        # user = User("test_user")',
            '',
            '        # Step 1: User logs in',
            '        # self.app.login(user)',
            '        # self.assertTrue(self.app.is_logged_in(user))',
            '',
            '        # Step 2: User performs an action',
            '        # result = self.app.perform_action(user, "action")',
            '        # self.assertEqual("success", result)',
            '',
            '        # Step 3: User views the result',
            '        # view = self.app.view_result(user)',
            '        # self.assertEqual("expected view", view)',
            '',
            '        # Step 4: User logs out',
            '        # self.app.logout(user)',
            '        # self.assertFalse(self.app.is_logged_in(user))',
            '        pass',
            '',
        ])

        # Add main block
        content.extend([
            '',
            "if __name__ == '__main__':",
            '    unittest.main()',
            '',
        ])

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
