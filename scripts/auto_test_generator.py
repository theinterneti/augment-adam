#!/usr/bin/env python3
"""
Automated Test Generator for Dukat

This script automates the generation of unit tests for Python modules using
local LLMs and test generation tools. It combines multiple approaches to create
comprehensive test suites.

Usage:
    python auto_test_generator.py --source-file path/to/file.py --output-dir tests/
"""

import os
import sys
import argparse
import subprocess
import logging
import json
import time
from pathlib import Path
import ast
import inspect
import importlib.util
from typing import Dict, List, Any, Optional, Tuple, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_generation.log"),
    ],
)
logger = logging.getLogger("auto_test_generator")

# Default configuration
DEFAULT_CONFIG = {
    "model_name": "codellama:7b",
    "ollama_host": "http://localhost:11434",
    "temperature": 0.2,
    "max_tokens": 2048,
    "test_frameworks": ["pytest", "hypothesis"],
    "use_pynguin": True,
    "use_llm": True,
    "max_retries": 3,
    "timeout": 300,  # seconds
}


class ModuleAnalyzer:
    """Analyzes Python modules to extract information for test generation."""

    def __init__(self, source_file: str):
        """Initialize the analyzer with a source file path."""
        self.source_file = source_file
        self.module_name = Path(source_file).stem
        self.module_path = str(Path(source_file).parent)
        self.ast_tree = None
        self.classes = []
        self.functions = []
        self.imports = []
        
        self._parse_source()
    
    def _parse_source(self):
        """Parse the source file and extract information."""
        try:
            with open(self.source_file, "r") as f:
                source = f.read()
            
            self.ast_tree = ast.parse(source)
            
            # Extract classes, functions, and imports
            for node in ast.walk(self.ast_tree):
                if isinstance(node, ast.ClassDef):
                    self.classes.append({
                        "name": node.name,
                        "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                        "line_number": node.lineno,
                    })
                elif isinstance(node, ast.FunctionDef) and node.parent_field != "body":
                    self.functions.append({
                        "name": node.name,
                        "args": [a.arg for a in node.args.args],
                        "line_number": node.lineno,
                    })
                elif isinstance(node, ast.Import):
                    self.imports.extend([n.name for n in node.names])
                elif isinstance(node, ast.ImportFrom):
                    self.imports.append(f"{node.module}.{node.names[0].name}")
            
            logger.info(f"Successfully parsed {self.source_file}")
            logger.info(f"Found {len(self.classes)} classes and {len(self.functions)} functions")
        
        except Exception as e:
            logger.error(f"Error parsing {self.source_file}: {str(e)}")
            raise
    
    def get_module_summary(self) -> Dict[str, Any]:
        """Get a summary of the module for test generation."""
        return {
            "module_name": self.module_name,
            "module_path": self.module_path,
            "classes": self.classes,
            "functions": self.functions,
            "imports": self.imports,
        }
    
    def load_module(self):
        """Dynamically load the module for inspection."""
        try:
            spec = importlib.util.spec_from_file_location(self.module_name, self.source_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.error(f"Error loading module {self.module_name}: {str(e)}")
            return None


class LLMTestGenerator:
    """Generates tests using a local LLM."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the LLM test generator with configuration."""
        self.config = config
        self.model_name = config.get("model_name", "codellama:7b")
        self.ollama_host = config.get("ollama_host", "http://localhost:11434")
        self.temperature = config.get("temperature", 0.2)
        self.max_tokens = config.get("max_tokens", 2048)
    
    def generate_tests(self, source_file: str, module_summary: Dict[str, Any]) -> str:
        """Generate tests for a module using a local LLM."""
        try:
            # Read the source file
            with open(source_file, "r") as f:
                source_code = f.read()
            
            # Create the prompt
            prompt = self._create_prompt(source_code, module_summary)
            
            # Call the LLM
            response = self._call_llm(prompt)
            
            # Extract the test code from the response
            test_code = self._extract_test_code(response)
            
            return test_code
        
        except Exception as e:
            logger.error(f"Error generating tests with LLM: {str(e)}")
            return ""
    
    def _create_prompt(self, source_code: str, module_summary: Dict[str, Any]) -> str:
        """Create a prompt for the LLM to generate tests."""
        prompt = f"""
You are an expert Python developer tasked with writing comprehensive unit tests.
Please generate pytest unit tests for the following Python module.

Source code:
```python
{source_code}
```

Module summary:
- Module name: {module_summary['module_name']}
- Classes: {', '.join([c['name'] for c in module_summary['classes']])}
- Functions: {', '.join([f['name'] for f in module_summary['functions']])}

Requirements:
1. Write comprehensive pytest tests that achieve high code coverage
2. Include tests for edge cases and error conditions
3. Use pytest fixtures where appropriate
4. Use parametrized tests for testing multiple inputs
5. Include docstrings explaining the purpose of each test
6. Follow best practices for Python testing

Please generate the complete test file content, including all necessary imports.
The test file should be named test_{module_summary['module_name']}.py.

Return only the Python code for the test file, without any additional explanations.
"""
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call the local LLM using Ollama."""
        import requests
        import json
        
        url = f"{self.ollama_host}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            raise
    
    def _extract_test_code(self, response: str) -> str:
        """Extract the test code from the LLM response."""
        # If the response contains code blocks, extract them
        if "```python" in response:
            code_blocks = []
            lines = response.split("\n")
            in_code_block = False
            
            for line in lines:
                if line.strip() == "```python":
                    in_code_block = True
                    continue
                elif line.strip() == "```" and in_code_block:
                    in_code_block = False
                    continue
                
                if in_code_block:
                    code_blocks.append(line)
            
            return "\n".join(code_blocks)
        
        # Otherwise, return the entire response
        return response


class PynguinTestGenerator:
    """Generates tests using Pynguin."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Pynguin test generator with configuration."""
        self.config = config
    
    def generate_tests(self, source_file: str, output_dir: str) -> bool:
        """Generate tests using Pynguin."""
        try:
            project_root = str(Path(source_file).parent)
            module_name = Path(source_file).stem
            
            cmd = [
                "pynguin",
                "--project-path", project_root,
                "--output-path", output_dir,
                "--module-name", module_name,
                "--algorithm", "DYNAMOSA",
                "--assertion-generation", "MUTATION",
                "--population", "50",
                "--budget", "60",
            ]
            
            logger.info(f"Running Pynguin: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
            )
            
            if result.returncode != 0:
                logger.warning(f"Pynguin exited with code {result.returncode}")
                logger.warning(f"Pynguin stderr: {result.stderr}")
                return False
            
            logger.info(f"Pynguin successfully generated tests in {output_dir}")
            return True
        
        except Exception as e:
            logger.error(f"Error generating tests with Pynguin: {str(e)}")
            return False


class HypothesisTestGenerator:
    """Generates property-based tests using Hypothesis."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Hypothesis test generator with configuration."""
        self.config = config
    
    def generate_tests(self, source_file: str, module_summary: Dict[str, Any]) -> str:
        """Generate property-based tests using Hypothesis."""
        try:
            test_code = []
            
            # Add imports
            test_code.append("import pytest")
            test_code.append("from hypothesis import given, strategies as st")
            test_code.append(f"from {module_summary['module_name']} import *")
            test_code.append("")
            
            # Generate tests for each class
            for class_info in module_summary["classes"]:
                class_name = class_info["name"]
                test_code.append(f"class Test{class_name}:")
                
                # Generate tests for each method
                for method_name in class_info["methods"]:
                    if method_name.startswith("__"):
                        continue
                    
                    test_code.append(f"    @given(st.integers(), st.integers())")
                    test_code.append(f"    def test_{method_name}_properties(self, a, b):")
                    test_code.append(f"        \"\"\"Test properties of {method_name} using Hypothesis.\"\"\"")
                    test_code.append(f"        instance = {class_name}()")
                    test_code.append(f"        # Add assertions based on expected properties")
                    test_code.append(f"        # This is a placeholder - customize based on the method's behavior")
                    test_code.append(f"        try:")
                    test_code.append(f"            result = instance.{method_name}(a, b)")
                    test_code.append(f"        except Exception as e:")
                    test_code.append(f"            # Handle expected exceptions")
                    test_code.append(f"            pass")
                    test_code.append("")
            
            # Generate tests for each function
            for func_info in module_summary["functions"]:
                func_name = func_info["name"]
                if func_name.startswith("_"):
                    continue
                
                test_code.append(f"@given(st.integers(), st.integers())")
                test_code.append(f"def test_{func_name}_properties(a, b):")
                test_code.append(f"    \"\"\"Test properties of {func_name} using Hypothesis.\"\"\"")
                test_code.append(f"    # Add assertions based on expected properties")
                test_code.append(f"    # This is a placeholder - customize based on the function's behavior")
                test_code.append(f"    try:")
                test_code.append(f"        result = {func_name}(a, b)")
                test_code.append(f"    except Exception as e:")
                test_code.append(f"        # Handle expected exceptions")
                test_code.append(f"        pass")
                test_code.append("")
            
            return "\n".join(test_code)
        
        except Exception as e:
            logger.error(f"Error generating Hypothesis tests: {str(e)}")
            return ""


class TestGenerator:
    """Main class for generating tests using multiple approaches."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the test generator with configuration."""
        self.config = config
        self.llm_generator = LLMTestGenerator(config)
        self.pynguin_generator = PynguinTestGenerator(config)
        self.hypothesis_generator = HypothesisTestGenerator(config)
    
    def generate_tests(self, source_file: str, output_dir: str) -> Dict[str, str]:
        """Generate tests for a source file using multiple approaches."""
        results = {}
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Analyze the module
        analyzer = ModuleAnalyzer(source_file)
        module_summary = analyzer.get_module_summary()
        
        # Generate tests using LLM
        if self.config.get("use_llm", True):
            logger.info(f"Generating tests using LLM for {source_file}")
            llm_tests = self.llm_generator.generate_tests(source_file, module_summary)
            
            if llm_tests:
                output_file = os.path.join(output_dir, f"test_{module_summary['module_name']}_llm.py")
                with open(output_file, "w") as f:
                    f.write(llm_tests)
                
                results["llm"] = output_file
                logger.info(f"LLM tests written to {output_file}")
        
        # Generate tests using Pynguin
        if self.config.get("use_pynguin", True):
            logger.info(f"Generating tests using Pynguin for {source_file}")
            pynguin_success = self.pynguin_generator.generate_tests(source_file, output_dir)
            
            if pynguin_success:
                results["pynguin"] = os.path.join(output_dir, f"test_{module_summary['module_name']}_pynguin.py")
                logger.info(f"Pynguin tests generated in {output_dir}")
        
        # Generate tests using Hypothesis
        if "hypothesis" in self.config.get("test_frameworks", []):
            logger.info(f"Generating property-based tests for {source_file}")
            hypothesis_tests = self.hypothesis_generator.generate_tests(source_file, module_summary)
            
            if hypothesis_tests:
                output_file = os.path.join(output_dir, f"test_{module_summary['module_name']}_hypothesis.py")
                with open(output_file, "w") as f:
                    f.write(hypothesis_tests)
                
                results["hypothesis"] = output_file
                logger.info(f"Hypothesis tests written to {output_file}")
        
        return results


def main():
    """Main function to run the test generator."""
    parser = argparse.ArgumentParser(description="Generate tests using multiple approaches")
    parser.add_argument("--source-file", required=True, help="Path to the source file")
    parser.add_argument("--output-dir", required=True, help="Directory to output generated tests")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM-based test generation")
    parser.add_argument("--no-pynguin", action="store_true", help="Skip Pynguin test generation")
    parser.add_argument("--no-hypothesis", action="store_true", help="Skip Hypothesis test generation")
    parser.add_argument("--model", help="LLM model to use (default: codellama:7b)")
    parser.add_argument("--ollama-host", help="Ollama host URL (default: http://localhost:11434)")
    
    args = parser.parse_args()
    
    # Load configuration
    config = DEFAULT_CONFIG.copy()
    
    if args.config:
        try:
            with open(args.config, "r") as f:
                config.update(json.load(f))
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
    
    # Override configuration with command-line arguments
    if args.no_llm:
        config["use_llm"] = False
    
    if args.no_pynguin:
        config["use_pynguin"] = False
    
    if args.no_hypothesis and "hypothesis" in config["test_frameworks"]:
        config["test_frameworks"].remove("hypothesis")
    
    if args.model:
        config["model_name"] = args.model
    
    if args.ollama_host:
        config["ollama_host"] = args.ollama_host
    
    # Generate tests
    generator = TestGenerator(config)
    results = generator.generate_tests(args.source_file, args.output_dir)
    
    # Print results
    logger.info("Test generation completed")
    logger.info(f"Generated test files: {list(results.values())}")


if __name__ == "__main__":
    main()
