#!/usr/bin/env python3
"""
Test Generator.

This module provides a test generator that uses Hugging Face models to
generate tests for Python modules.
"""

import asyncio
import logging
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logger = logging.getLogger("test_generator")


class TestGenerator:
    """Test generator that uses Hugging Face models to generate tests."""

    def __init__(
        self,
        model_name: str = "mistralai/Mistral-7B-Instruct-v0.2",
        cache_dir: Optional[str] = None,
        use_gpu: bool = True,
        temperature: float = 0.2,
        max_length: int = 2048,
    ):
        """Initialize the test generator.

        Args:
            model_name: Name of the Hugging Face model to use
            cache_dir: Directory to cache models
            use_gpu: Whether to use GPU acceleration
            temperature: Temperature for text generation
            max_length: Maximum length of generated text
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.use_gpu = use_gpu
        self.temperature = temperature
        self.max_length = max_length
        self.model = None
        self.tokenizer = None

    async def generate_tests(
        self, file_path: str, output_dir: str, merge: bool = True
    ) -> Optional[str]:
        """Generate tests for a file.

        Args:
            file_path: Path to the file to generate tests for
            output_dir: Directory to save the test files
            merge: Whether to merge with existing tests

        Returns:
            Path to the generated test file, or None if generation failed
        """
        try:
            # Load the model if not already loaded
            if self.model is None:
                await self._load_model()

            # Read the file content
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Generate the test file path
            rel_path = os.path.relpath(file_path, "src")
            module_dir = os.path.dirname(rel_path)
            module_name = os.path.basename(file_path).replace(".py", "")
            test_dir = os.path.join(output_dir, "unit", module_dir)
            test_file_path = os.path.join(test_dir, f"test_{module_name}.py")

            # Create the output directory if it doesn't exist
            os.makedirs(test_dir, exist_ok=True)

            # Check if the test file already exists
            existing_content = None
            if os.path.exists(test_file_path) and merge:
                with open(test_file_path, "r", encoding="utf-8") as f:
                    existing_content = f.read()

            # Generate the test content
            test_content = await self._generate_test_content(
                file_path, file_content, existing_content
            )

            if not test_content:
                logger.warning(f"Failed to generate test content for {file_path}")
                return None

            # Write the test content to the file
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(test_content)

            logger.info(f"Generated tests saved to: {test_file_path}")
            return test_file_path

        except Exception as e:
            logger.error(f"Error generating tests for {file_path}: {e}", exc_info=True)
            return None

    async def _load_model(self):
        """Load the Hugging Face model."""
        try:
            # Import here to avoid loading transformers at module import time
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            from huggingface_hub import login
            import os

            logger.info(f"Loading model {self.model_name}")

            # Check for Hugging Face token and login if available
            hf_token = os.environ.get("HUGGING_FACE_HUB_TOKEN")
            if hf_token:
                logger.info("Logging in to Hugging Face with token from environment")
                login(hf_token)

            # Determine the device
            device = "cuda" if torch.cuda.is_available() and self.use_gpu else "cpu"
            logger.info(f"Using device: {device}")

            # Load the tokenizer with trust_remote_code for Qwen models
            trust_remote_code = "qwen" in self.model_name.lower()
            logger.info(f"Using trust_remote_code={trust_remote_code}")

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                trust_remote_code=trust_remote_code
            )

            # Load the model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                low_cpu_mem_usage=True,
                trust_remote_code=trust_remote_code
            )

            if device == "cpu":
                self.model = self.model.to(device)

            logger.info(f"Model {self.model_name} loaded successfully")

        except Exception as e:
            logger.error(f"Error loading model: {e}", exc_info=True)
            raise

    async def _generate_test_content(
        self, file_path: str, file_content: str, existing_content: Optional[str] = None
    ) -> Optional[str]:
        """Generate test content for a file.

        Args:
            file_path: Path to the file
            file_content: Content of the file
            existing_content: Existing test content to merge with

        Returns:
            Generated test content
        """
        try:
            # Create the prompt
            prompt = self._create_test_prompt(file_path, file_content, existing_content)

            # Generate the test content
            loop = asyncio.get_event_loop()
            test_content = await loop.run_in_executor(
                None, self._generate_text, prompt
            )

            if not test_content:
                return None

            # Extract the Python code from the response
            test_content = self._extract_python_code(test_content)

            # Post-process the test content
            test_content = self._post_process_test_content(
                test_content, file_path, existing_content
            )

            return test_content

        except Exception as e:
            logger.error(f"Error generating test content: {e}", exc_info=True)
            return None

    def _create_test_prompt(
        self, file_path: str, file_content: str, existing_content: Optional[str] = None
    ) -> str:
        """Create a prompt for test generation.

        Args:
            file_path: Path to the file
            file_content: Content of the file
            existing_content: Existing test content to merge with

        Returns:
            Prompt for test generation
        """
        module_name = os.path.basename(file_path).replace(".py", "")
        module_path = os.path.relpath(file_path, "src").replace("/", ".").replace(".py", "")

        # Format for Qwen instruction models
        system_message = """You are an expert Python developer specializing in test-driven development.
Your task is to write comprehensive, high-quality unit tests for Python modules."""

        user_message = f"""I need you to write a complete pytest test file for the following Python module:

```python
{file_content}
```

The test file should:
1. Import the necessary modules, including pytest, unittest.mock, and the module being tested
2. Create test classes for each class in the module
3. Create test methods for each method in each class
4. Include appropriate assertions to verify the behavior
5. Use mocks and patches where appropriate to isolate the unit being tested
6. Handle edge cases and error conditions
7. Include docstrings for each test class and method

The test file should be named test_{module_name}.py and should be placed in the appropriate directory.
"""

        if existing_content:
            user_message += f"""
Here is the existing test file content that you should merge with:

```python
{existing_content}
```

Merge your new tests with the existing tests, preserving any custom test methods and fixtures.
Only add new tests for functionality that is not already covered.
"""

        user_message += """
Please provide only the Python code for the test file, without any additional explanation.
"""

        # Format the prompt for Qwen models
        prompt = f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant\n"

        return prompt

    def _generate_text(self, prompt: str) -> Optional[str]:
        """Generate text using the Hugging Face model.

        Args:
            prompt: Prompt for text generation

        Returns:
            Generated text
        """
        try:
            import torch

            # Tokenize the prompt
            inputs = self.tokenizer(prompt, return_tensors="pt")
            input_ids = inputs["input_ids"].to(self.model.device)

            # Generate text
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids,
                    max_length=self.max_length,
                    temperature=self.temperature,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            # Decode the generated text
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract the assistant's response from the Qwen format
            if "<|im_start|>assistant\n" in generated_text:
                # Extract text after the assistant tag
                generated_text = generated_text.split("<|im_start|>assistant\n", 1)[1]

                # Remove any trailing tags
                if "<|im_end|>" in generated_text:
                    generated_text = generated_text.split("<|im_end|>", 1)[0]
            # Fallback for other formats
            elif generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()

            return generated_text

        except Exception as e:
            logger.error(f"Error generating text: {e}", exc_info=True)
            return None

    def _extract_python_code(self, text: str) -> str:
        """Extract Python code from text.

        Args:
            text: Text containing Python code

        Returns:
            Extracted Python code
        """
        # Extract code between triple backticks
        code_blocks = re.findall(r"```python(.*?)```", text, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()

        # If no code blocks, try to extract based on indentation
        lines = text.split("\n")
        code_lines = []
        in_code = False
        for line in lines:
            if line.strip().startswith("def ") or line.strip().startswith("class "):
                in_code = True
            if in_code:
                code_lines.append(line)
        if code_lines:
            return "\n".join(code_lines)

        # If all else fails, return the original text
        return text

    def _post_process_test_content(
        self, test_content: str, file_path: str, existing_content: Optional[str] = None
    ) -> str:
        """Post-process the generated test content.

        Args:
            test_content: Generated test content
            file_path: Path to the file
            existing_content: Existing test content

        Returns:
            Post-processed test content
        """
        # Add imports if missing
        if "import pytest" not in test_content:
            test_content = "import pytest\n" + test_content

        if "unittest.mock" not in test_content and "mock" not in test_content:
            test_content = "from unittest.mock import patch, MagicMock\n" + test_content

        # Add the module import if missing
        module_path = os.path.relpath(file_path, "src").replace("/", ".").replace(".py", "")
        if module_path not in test_content:
            import_line = f"from {module_path} import *\n"
            test_content = import_line + test_content

        # Add docstrings if missing
        if '"""' not in test_content:
            module_name = os.path.basename(file_path).replace(".py", "")
            docstring = f'"""\nUnit tests for {module_name}.\n"""\n\n'
            test_content = docstring + test_content

        return test_content


if __name__ == "__main__":
    # Simple test
    import argparse

    parser = argparse.ArgumentParser(description="Generate tests for a Python file")
    parser.add_argument("--file", required=True, help="Path to the Python file")
    parser.add_argument("--output-dir", default="tests", help="Directory to save the test files")
    parser.add_argument("--model", default="Qwen/Qwen2-7B-Instruct", help="Name of the Hugging Face model to use")
    parser.add_argument("--no-gpu", action="store_true", help="Disable GPU acceleration")
    parser.add_argument("--temperature", type=float, default=0.2, help="Temperature for text generation")
    parser.add_argument("--merge", action="store_true", default=True, help="Merge with existing tests")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    generator = TestGenerator(
        model_name=args.model,
        use_gpu=not args.no_gpu,
        temperature=args.temperature,
    )

    asyncio.run(generator.generate_tests(args.file, args.output_dir, merge=args.merge))
