#!/usr/bin/env python3
"""
Generate tests for priority areas.

This script generates tests for specific files in the priority areas.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("generate_priority_tests")

# Priority files to test
PRIORITY_FILES = [
    # Memory System
    "src/augment_adam/memory/core/base.py",
    "src/augment_adam/memory/vector/base.py",
    "src/augment_adam/memory/vector/faiss.py",
    "src/augment_adam/memory/vector/chroma.py",
    "src/augment_adam/memory/graph/base.py",
    "src/augment_adam/memory/graph/neo4j.py",
    "src/augment_adam/memory/graph/networkx.py",
    "src/augment_adam/memory/episodic/base.py",
    "src/augment_adam/memory/semantic/base.py",
    "src/augment_adam/memory/working/base.py",
    
    # Context Engine
    "src/augment_adam/context/core/base.py",
    "src/augment_adam/context/chunking/base.py",
    "src/augment_adam/context/composition/base.py",
    "src/augment_adam/context/retrieval/base.py",
    "src/augment_adam/context/prompt/base.py",
    "src/augment_adam/context/storage/base.py",
    
    # Monte Carlo Methods
    "src/augment_adam/monte_carlo/mcmc/base.py",
    "src/augment_adam/monte_carlo/mcmc/samplers.py",
    "src/augment_adam/monte_carlo/mcmc/proposals.py",
    "src/augment_adam/monte_carlo/mcts/base.py",
    "src/augment_adam/monte_carlo/mcts/policies.py",
    "src/augment_adam/monte_carlo/particle_filter/base.py",
    "src/augment_adam/monte_carlo/particle_filter/models.py",
    "src/augment_adam/monte_carlo/particle_filter/resampling.py",
    "src/augment_adam/monte_carlo/sequential_mc/base.py",
    "src/augment_adam/monte_carlo/sequential_mc/models.py",
    "src/augment_adam/monte_carlo/importance_sampling/base.py",
    "src/augment_adam/monte_carlo/importance_sampling/adaptive.py",
    "src/augment_adam/monte_carlo/utils/distributions.py",
    "src/augment_adam/monte_carlo/utils/statistics.py",
    
    # Parallel Processing
    "src/augment_adam/parallel/base.py",
    "src/augment_adam/parallel/thread/base.py",
    "src/augment_adam/parallel/process/base.py",
    "src/augment_adam/parallel/async_module/base.py",
    "src/augment_adam/parallel/workflow/base.py",
    "src/augment_adam/parallel/utils/errors.py",
    "src/augment_adam/parallel/utils/resources.py",
    "src/augment_adam/parallel/utils/results.py",
]

def generate_test_for_file(file_path: str, output_dir: str = "tests/unit") -> str:
    """
    Generate a test file for a Python file.
    
    Args:
        file_path: Path to the Python file
        output_dir: Directory to save the test file
        
    Returns:
        Path to the generated test file
    """
    # Determine the output directory based on the file path
    rel_path = os.path.relpath(file_path, "src/augment_adam")
    module_dir = os.path.dirname(rel_path)
    module_output_dir = os.path.join(output_dir, module_dir)
    
    # Create the output directory if it doesn't exist
    os.makedirs(module_output_dir, exist_ok=True)
    
    # Generate the test file
    cmd = ["python", "scripts/enhanced_test_generator.py", "--file", file_path, "--output-dir", module_output_dir]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Extract the output file path
        for line in result.stdout.split('\n'):
            if "Generated unit tests saved to:" in line:
                test_file_path = line.split("Generated unit tests saved to:")[1].strip()
                return test_file_path
        
        # If we couldn't extract the path, construct it
        module_name = os.path.basename(file_path).replace('.py', '')
        test_file_path = os.path.join(module_output_dir, f"test_{module_name}.py")
        return test_file_path
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating test for {file_path}: {e}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        return None

def main():
    """Run the test generator for priority files."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate tests for priority files")
    parser.add_argument("--output-dir", default="tests/unit", help="Directory to save the test files (default: tests/unit)")
    parser.add_argument("--file", help="Generate tests for a specific file")
    args = parser.parse_args()
    
    # Generate tests for a specific file or all priority files
    if args.file:
        if not os.path.exists(args.file):
            logger.error(f"File not found: {args.file}")
            return
        
        logger.info(f"Generating test for {args.file}")
        test_file_path = generate_test_for_file(args.file, args.output_dir)
        
        if test_file_path:
            logger.info(f"Generated test file: {test_file_path}")
        else:
            logger.error(f"Failed to generate test for {args.file}")
    
    else:
        # Generate tests for all priority files
        generated_files = []
        
        for file_path in PRIORITY_FILES:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue
            
            logger.info(f"Generating test for {file_path}")
            test_file_path = generate_test_for_file(file_path, args.output_dir)
            
            if test_file_path:
                logger.info(f"Generated test file: {test_file_path}")
                generated_files.append(test_file_path)
            else:
                logger.error(f"Failed to generate test for {file_path}")
        
        logger.info(f"Generated {len(generated_files)} test files")

if __name__ == "__main__":
    main()
