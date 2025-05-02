#!/usr/bin/env python3
"""
Test Qwen Model.

This script tests the Qwen model to ensure it's working correctly for test generation.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.test_generator import TestGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("test_qwen_model")


async def test_model(model_name: str, use_gpu: bool = True):
    """Test the Qwen model for test generation.

    Args:
        model_name: Name of the Qwen model to test
        use_gpu: Whether to use GPU acceleration
    """
    logger.info(f"Testing model: {model_name}")

    # Create a simple Python file to test
    test_file = "temp_test_file.py"
    with open(test_file, "w") as f:
        f.write("""
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def subtract(a, b):
    \"\"\"Subtract b from a.\"\"\"
    return a - b

class Calculator:
    \"\"\"A simple calculator class.\"\"\"

    def __init__(self, initial_value=0):
        \"\"\"Initialize the calculator.\"\"\"
        self.value = initial_value

    def add(self, x):
        \"\"\"Add x to the current value.\"\"\"
        self.value += x
        return self.value

    def subtract(self, x):
        \"\"\"Subtract x from the current value.\"\"\"
        self.value -= x
        return self.value

    def reset(self):
        \"\"\"Reset the calculator to zero.\"\"\"
        self.value = 0
        return self.value
""")

    try:
        # Create the test generator
        generator = TestGenerator(
            model_name=model_name,
            use_gpu=use_gpu,
            temperature=0.2,
        )

        # Generate tests
        logger.info("Generating tests...")
        output_dir = "temp_test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        test_file_path = await generator.generate_tests(test_file, output_dir)
        
        if test_file_path:
            logger.info(f"Successfully generated tests at: {test_file_path}")
            
            # Display the generated test file
            with open(test_file_path, "r") as f:
                test_content = f.read()
            
            logger.info("Generated test content:")
            print("\n" + "=" * 80)
            print(test_content)
            print("=" * 80 + "\n")
            
            return True
        else:
            logger.error("Failed to generate tests")
            return False

    except Exception as e:
        logger.error(f"Error testing model: {e}", exc_info=True)
        return False
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)


async def main():
    """Run the Qwen model test."""
    parser = argparse.ArgumentParser(description="Test Qwen model for test generation")
    parser.add_argument("--model", default="Qwen/Qwen2-7B-Instruct", help="Name of the Qwen model to test")
    parser.add_argument("--no-gpu", action="store_true", help="Disable GPU acceleration")
    args = parser.parse_args()

    success = await test_model(args.model, not args.no_gpu)
    
    if success:
        logger.info("Model test successful")
        sys.exit(0)
    else:
        logger.error("Model test failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
