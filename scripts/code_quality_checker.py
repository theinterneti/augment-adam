#!/usr/bin/env python3
"""
Code Quality Checker.

This script analyzes Python code files against the project's code quality checklist
and generates a report of which checklist items pass and which need attention.
"""

import argparse
import ast
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


class CodeQualityChecker:
    """
    Analyzes Python code files against the project's code quality checklist.
    """

    def __init__(self, file_path: str):
        """
        Initialize the checker with a file path.

        Args:
            file_path: Path to the Python file to check
        """
        self.file_path = file_path
        self.file_content = ""
        self.ast_tree = None
        self.issues = []
        self.passes = []

        # Load the file content
        self._load_file()

    def _load_file(self) -> None:
        """Load the file content and parse the AST."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.file_content = f.read()

            self.ast_tree = ast.parse(self.file_content)
        except Exception as e:
            self.issues.append(f"Error loading file: {e}")

    def check_all(self) -> Tuple[List[str], List[str]]:
        """
        Run all checks on the file.

        Returns:
            A tuple of (passes, issues)
        """
        # Documentation checks
        self._check_module_docstring()
        self._check_class_docstrings()
        self._check_function_docstrings()
        self._check_google_style()
        self._check_todo_comments()

        # Type hint checks
        self._check_function_type_hints()
        self._check_return_type_hints()

        # Testing checks
        self._check_test_file_exists()

        # Code style checks
        self._check_line_length()
        self._check_naming_conventions()

        # Tagging checks
        self._check_module_tags()
        self._check_class_tags()

        # GitHub integration checks
        self._check_issue_references()

        return self.passes, self.issues

    def _check_module_docstring(self) -> None:
        """Check if the module has a docstring."""
        if self.ast_tree and ast.get_docstring(self.ast_tree):
            self.passes.append("Module has a docstring")
        else:
            self.issues.append("Module is missing a docstring")

    def _check_class_docstrings(self) -> None:
        """Check if all classes have docstrings."""
        if not self.ast_tree:
            return

        classes = [node for node in ast.walk(self.ast_tree) if isinstance(node, ast.ClassDef)]

        for cls in classes:
            if ast.get_docstring(cls):
                self.passes.append(f"Class '{cls.name}' has a docstring")
            else:
                self.issues.append(f"Class '{cls.name}' is missing a docstring")

    def _check_function_docstrings(self) -> None:
        """Check if all functions and methods have docstrings."""
        if not self.ast_tree:
            return

        functions = [node for node in ast.walk(self.ast_tree)
                    if isinstance(node, ast.FunctionDef)]

        for func in functions:
            # Skip special methods like __init__ that often inherit docstrings
            if func.name.startswith('__') and func.name.endswith('__'):
                continue

            if ast.get_docstring(func):
                self.passes.append(f"Function '{func.name}' has a docstring")
            else:
                self.issues.append(f"Function '{func.name}' is missing a docstring")

    def _check_google_style(self) -> None:
        """Check if docstrings follow Google style."""
        if not self.ast_tree:
            return

        # Get all nodes with docstrings
        nodes_with_docstrings = []

        # Module docstring
        if ast.get_docstring(self.ast_tree):
            nodes_with_docstrings.append(("Module", None, ast.get_docstring(self.ast_tree)))

        # Class docstrings
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef) and ast.get_docstring(node):
                nodes_with_docstrings.append(("Class", node.name, ast.get_docstring(node)))
            elif isinstance(node, ast.FunctionDef) and ast.get_docstring(node):
                nodes_with_docstrings.append(("Function", node.name, ast.get_docstring(node)))

        # Check each docstring for Google style patterns
        for node_type, name, docstring in nodes_with_docstrings:
            # Look for Google style sections like Args:, Returns:, Raises:
            google_style_sections = re.findall(r'(Args|Returns|Raises|Attributes|Examples):', docstring)

            if google_style_sections:
                self.passes.append(f"{node_type} {name or ''} docstring follows Google style")
            else:
                self.issues.append(f"{node_type} {name or ''} docstring may not follow Google style")

    def _check_todo_comments(self) -> None:
        """Check if TODO comments include issue numbers."""
        if not self.file_content:
            return

        # Find all TODO comments
        todo_comments = re.findall(r'#\s*TODO\b(.*)', self.file_content)

        for comment in todo_comments:
            # Check if the comment includes an issue reference like (Issue #123)
            if re.search(r'\(Issue\s+#\d+\)', comment):
                self.passes.append("TODO comment includes issue reference")
            else:
                self.issues.append(f"TODO comment missing issue reference: {comment.strip()}")

    def _check_function_type_hints(self) -> None:
        """Check if functions have parameter type hints."""
        if not self.ast_tree:
            return

        functions = [node for node in ast.walk(self.ast_tree)
                    if isinstance(node, ast.FunctionDef)]

        for func in functions:
            # Skip special methods like __init__ that often inherit docstrings
            if func.name.startswith('__') and func.name.endswith('__'):
                continue

            # Check if all parameters have type annotations
            missing_type_hints = []

            for arg in func.args.args:
                # In Python 3.8+, the attribute is 'arg'
                arg_name = getattr(arg, 'arg', getattr(arg, 'name', None))

                if arg_name == 'self' or arg_name == 'cls':
                    continue

                if arg.annotation is None:
                    missing_type_hints.append(arg_name)

            if missing_type_hints:
                self.issues.append(f"Function '{func.name}' is missing type hints for parameters: {', '.join(missing_type_hints)}")
            else:
                self.passes.append(f"Function '{func.name}' has type hints for all parameters")

    def _check_return_type_hints(self) -> None:
        """Check if functions have return type hints."""
        if not self.ast_tree:
            return

        functions = [node for node in ast.walk(self.ast_tree)
                    if isinstance(node, ast.FunctionDef)]

        for func in functions:
            # Skip special methods like __init__ that often don't need return type hints
            if func.name == '__init__':
                continue

            if func.returns is None:
                self.issues.append(f"Function '{func.name}' is missing a return type hint")
            else:
                self.passes.append(f"Function '{func.name}' has a return type hint")

    def _check_test_file_exists(self) -> None:
        """Check if a test file exists for this module."""
        if not self.file_path:
            return

        # Determine the expected test file path
        file_name = os.path.basename(self.file_path)
        module_name = os.path.splitext(file_name)[0]

        # Skip if this is already a test file
        if module_name.startswith('test_'):
            self.passes.append("This is a test file")
            return

        # Look for test files in the tests directory
        project_root = Path(__file__).parent.parent
        possible_test_paths = [
            project_root / 'tests' / 'unit' / f'test_{module_name}.py',
            project_root / 'tests' / 'integration' / f'test_{module_name}.py',
            project_root / 'tests' / 'e2e' / f'test_{module_name}.py',
        ]

        for test_path in possible_test_paths:
            if test_path.exists():
                self.passes.append(f"Test file exists at {test_path.relative_to(project_root)}")
                return

        self.issues.append(f"No test file found for module '{module_name}'")

    def _check_line_length(self) -> None:
        """Check if any lines exceed the maximum length."""
        if not self.file_content:
            return

        max_length = 88  # As specified in the project guidelines

        long_lines = []
        for i, line in enumerate(self.file_content.splitlines(), 1):
            if len(line) > max_length:
                long_lines.append(i)

        if long_lines:
            self.issues.append(f"Lines exceeding {max_length} characters: {', '.join(map(str, long_lines))}")
        else:
            self.passes.append(f"All lines are within the {max_length} character limit")

    def _check_naming_conventions(self) -> None:
        """Check if naming conventions are followed."""
        if not self.ast_tree:
            return

        # Check class names (should be CamelCase)
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    self.issues.append(f"Class name '{node.name}' does not follow CamelCase convention")
                else:
                    self.passes.append(f"Class name '{node.name}' follows CamelCase convention")

            # Check function names (should be snake_case)
            elif isinstance(node, ast.FunctionDef):
                # Skip special methods
                if node.name.startswith('__') and node.name.endswith('__'):
                    continue

                if not re.match(r'^[a-z][a-z0-9_]*$', node.name):
                    self.issues.append(f"Function name '{node.name}' does not follow snake_case convention")
                else:
                    self.passes.append(f"Function name '{node.name}' follows snake_case convention")

            # Check variable names (should be snake_case)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Skip constants (all uppercase) and special variables like __all__
                        if target.id.isupper() or (target.id.startswith('__') and target.id.endswith('__')):
                            continue

                        if not re.match(r'^[a-z][a-z0-9_]*$', target.id):
                            self.issues.append(f"Variable name '{target.id}' does not follow snake_case convention")

    def _check_module_tags(self) -> None:
        """Check if the module has appropriate tags."""
        # This is a placeholder for the actual implementation
        # In a real implementation, we would check for tags in the module docstring
        pass

    def _check_class_tags(self) -> None:
        """Check if classes have appropriate tags."""
        # This is a placeholder for the actual implementation
        # In a real implementation, we would check for tags in class docstrings
        pass

    def _check_issue_references(self) -> None:
        """Check if the code references GitHub issues."""
        if not self.file_content:
            return

        # Look for issue references like #123 or (Issue #123)
        issue_refs = re.findall(r'(?:Issue\s+)?#\d+', self.file_content)

        if issue_refs:
            self.passes.append(f"Code references GitHub issues: {', '.join(issue_refs)}")
        else:
            self.issues.append("No GitHub issue references found")

    def generate_report(self) -> str:
        """
        Generate a report of the code quality check results.

        Returns:
            A formatted string report
        """
        passes, issues = self.check_all()

        report = [
            f"# Code Quality Report for {self.file_path}",
            "",
            f"## Summary",
            f"- Passes: {len(passes)}",
            f"- Issues: {len(issues)}",
            "",
        ]

        if passes:
            report.extend([
                "## Passes",
                ""
            ])
            for item in passes:
                report.append(f"- ✅ {item}")
            report.append("")

        if issues:
            report.extend([
                "## Issues",
                ""
            ])
            for item in issues:
                report.append(f"- ❌ {item}")
            report.append("")

        report.extend([
            "## Next Steps",
            "",
            "1. Address the issues identified in this report",
            "2. Run the checker again to verify fixes",
            "3. Once all critical issues are resolved, generate tests using `scripts/generate_tests.py`",
            ""
        ])

        return "\n".join(report)


def main():
    """Run the code quality checker on a file."""
    parser = argparse.ArgumentParser(description="Check code quality against project standards")
    parser.add_argument("--file", required=True, help="Path to the Python file to check")
    parser.add_argument("--output", help="Path to save the report (default: print to stdout)")
    args = parser.parse_args()

    checker = CodeQualityChecker(args.file)
    report = checker.generate_report()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
