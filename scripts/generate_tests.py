#!/usr/bin/env python
"""
Automated Test Generator Script.

This script analyzes Python modules and generates test stubs for untested functions.
It can run asynchronously and automatically build out the test suite without manual intervention.

Features:
- Asynchronous test generation
- Automatic discovery of untested modules
- Scheduled execution
- Configurable output
- Test suite building
"""

import os
import sys
import inspect
import importlib
import argparse
import asyncio
import logging
import time
import json
import pkgutil
import concurrent.futures
import datetime
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple, Union, Iterable

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / 'test_generator.log')
    ]
)
logger = logging.getLogger('test_generator')

def discover_modules(package_name: str) -> List[str]:
    """
    Discover all modules in a package recursively.

    Args:
        package_name: The name of the package to scan (e.g., 'augment_adam')

    Returns:
        A list of module paths
    """
    try:
        package = importlib.import_module(package_name)
        package_path = getattr(package, '__path__', [])

        if not package_path:
            return [package_name]

        modules = []

        for _, name, is_pkg in pkgutil.iter_modules(package_path):
            full_name = f"{package_name}.{name}"

            if is_pkg:
                # Recursively discover modules in subpackages
                modules.extend(discover_modules(full_name))
            else:
                modules.append(full_name)

        return modules
    except ImportError as e:
        logger.error(f"Error importing package {package_name}: {e}")
        return []

def get_module_functions(module_path: str) -> Dict[str, Any]:
    """
    Get all functions and classes in a module.

    Args:
        module_path: The import path of the module (e.g., 'augment_adam.memory.faiss_memory')

    Returns:
        A dictionary mapping function/class names to their objects
    """
    try:
        # Temporarily disable tag creation to avoid conflicts
        # This is a workaround for the "Tag already exists" error
        if 'augment_adam.utils.tagging.core' in sys.modules:
            tagging_module = sys.modules['augment_adam.utils.tagging.core']
            if hasattr(tagging_module, 'get_tag_registry'):
                # Save the original function
                original_create_tag = getattr(tagging_module.get_tag_registry(), 'create_tag', None)

                # Replace with a dummy function that doesn't raise errors
                if original_create_tag:
                    def dummy_create_tag(name, category, parent, attributes=None):
                        # Just return a dummy tag object
                        return parent

                    # Patch the function
                    tagging_module.get_tag_registry().create_tag = dummy_create_tag

        # Import the module
        module = importlib.import_module(module_path)

        # Get all functions and classes
        members = inspect.getmembers(module)

        # Filter to only include functions and classes defined in this module
        module_members = {}
        for name, obj in members:
            if (inspect.isfunction(obj) or inspect.isclass(obj)) and obj.__module__ == module_path:
                module_members[name] = obj

        # Restore the original function if we patched it
        if 'augment_adam.utils.tagging.core' in sys.modules and original_create_tag:
            tagging_module.get_tag_registry().create_tag = original_create_tag

        return module_members
    except ImportError as e:
        logger.error(f"Error importing module {module_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error processing module {module_path}: {e}")
        return {}

def get_existing_tests(test_dir: str) -> Set[str]:
    """
    Get the names of functions and classes that already have tests.

    Args:
        test_dir: The directory containing test files

    Returns:
        A set of function/class names that have tests
    """
    tested_items = set()

    # Walk through the test directory
    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                # Read the file and look for test_* functions
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = f.read()

                # Look for test_function_name patterns
                for line in content.split("\n"):
                    if line.strip().startswith("def test_"):
                        # Extract the function name being tested
                        test_name = line.strip().split("def test_")[1].split("(")[0]
                        tested_items.add(test_name)

                    # Also look for class tests
                    if "class Test" in line:
                        class_name = line.split("class Test")[1].split("(")[0]
                        tested_items.add(class_name)

    return tested_items

def generate_function_test_file(module_path: str, function_name: str, output_dir: str) -> str:
    """
    Generate a test file for a standalone function.

    Args:
        module_path: The import path of the module
        function_name: The name of the function to test
        output_dir: The directory to write the test file to

    Returns:
        The path to the generated test file
    """
    # Load the templates
    template_dir = Path(__file__).parent.parent / "src" / "augment_adam" / "testing" / "templates"

    with open(template_dir / "function_test_template.py", "r") as f:
        function_template = f.read()

    # Format the function template
    module_name = module_path.split(".")[-1]
    tag_path = ".".join(module_path.split(".")[1:])  # Remove the 'augment_adam' prefix

    test_file_content = function_template.format(
        module_name=module_name,
        import_path=module_path,
        function_name=function_name,
        tag_path=f"{tag_path}.{function_name.lower()}"
    )

    # Create the output directory structure
    module_parts = module_path.split(".")
    if module_parts[0] == "augment_adam":
        module_parts = module_parts[1:]  # Remove the 'augment_adam' prefix

    test_dir = Path(output_dir)
    for part in module_parts[:-1]:  # Exclude the last part (module name)
        test_dir = test_dir / part

    os.makedirs(test_dir, exist_ok=True)

    # Write the test file
    output_file = test_dir / f"test_{function_name.lower()}.py"
    with open(output_file, "w") as f:
        f.write(test_file_content)

    logger.info(f"Generated function test file: {output_file}")
    return str(output_file)

async def generate_test_file(module_path: str, class_name: str, methods: List[str], output_dir: str) -> str:
    """
    Generate a test file for a class asynchronously.

    Args:
        module_path: The import path of the module
        class_name: The name of the class to test
        methods: List of method names to test
        output_dir: The directory to write the test file to

    Returns:
        The path to the generated test file
    """
    # Load the templates
    template_dir = Path(__file__).parent.parent / "src" / "augment_adam" / "testing" / "templates"

    # Use a thread pool for file I/O operations
    with concurrent.futures.ThreadPoolExecutor() as pool:
        # Load templates in parallel
        class_template_future = pool.submit(
            lambda: open(template_dir / "unit_test_template.py", "r").read()
        )
        method_template_future = pool.submit(
            lambda: open(template_dir / "test_method_template.py", "r").read()
        )

        # Wait for templates to load
        class_template = await asyncio.wrap_future(class_template_future)
        method_template = await asyncio.wrap_future(method_template_future)

    # Generate test methods
    test_methods = []
    for method in methods:
        if method.startswith("_"):
            continue  # Skip private methods

        test_methods.append(method_template.format(
            method_name=method,
            instance_name=class_name.lower()
        ))

    # Format the class template
    module_name = module_path.split(".")[-1]
    tag_path = ".".join(module_path.split(".")[1:])  # Remove the 'augment_adam' prefix

    test_file_content = class_template.format(
        module_name=module_name,
        import_path=module_path,
        class_name=class_name,
        test_class_name=f"Test{class_name}",
        tag_path=f"{tag_path}.{class_name.lower()}",
        instance_name=class_name.lower(),
        test_methods="\n".join(test_methods)
    )

    # Create the output directory structure
    module_parts = module_path.split(".")
    if module_parts[0] == "augment_adam":
        module_parts = module_parts[1:]  # Remove the 'augment_adam' prefix

    test_dir = Path(output_dir)
    for part in module_parts[:-1]:  # Exclude the last part (module name)
        test_dir = test_dir / part

    os.makedirs(test_dir, exist_ok=True)

    # Write the test file
    output_file = test_dir / f"test_{class_name.lower()}.py"

    # Use a thread pool for file I/O operations
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await asyncio.wrap_future(
            pool.submit(lambda: open(output_file, "w").write(test_file_content))
        )

    logger.info(f"Generated class test file: {output_file}")
    return str(output_file)

async def process_module(module_path: str, output_dir: str, existing_tests: Set[str]) -> List[str]:
    """
    Process a module and generate tests for untested functions and classes.

    Args:
        module_path: The import path of the module
        output_dir: The directory to write test files to
        existing_tests: Set of names that already have tests

    Returns:
        List of paths to generated test files
    """
    logger.info(f"Processing module: {module_path}")

    # Get functions and classes in the module
    module_members = get_module_functions(module_path)

    # Track generated test files
    generated_files = []

    # Generate test stubs for untested classes
    class_tasks = []
    for name, obj in module_members.items():
        if inspect.isclass(obj) and name not in existing_tests:
            # Get methods of the class
            methods = [m[0] for m in inspect.getmembers(obj, predicate=inspect.isfunction)]

            # Generate a test file for the class
            class_tasks.append(generate_test_file(module_path, name, methods, output_dir))

    # Wait for all class test files to be generated
    if class_tasks:
        class_results = await asyncio.gather(*class_tasks)
        generated_files.extend(class_results)

    # Generate test stubs for untested functions
    for name, obj in module_members.items():
        if inspect.isfunction(obj) and name not in existing_tests:
            # Generate a test file for the function
            function_file = generate_function_test_file(module_path, name, output_dir)
            generated_files.append(function_file)

    return generated_files

async def generate_tests_for_package(package_name: str, output_dir: str) -> List[str]:
    """
    Generate tests for all modules in a package.

    Args:
        package_name: The name of the package to scan
        output_dir: The directory to write test files to

    Returns:
        List of paths to generated test files
    """
    logger.info(f"Generating tests for package: {package_name}")

    # Discover all modules in the package
    modules = discover_modules(package_name)
    logger.info(f"Discovered {len(modules)} modules in {package_name}")

    # Get existing tests
    existing_tests = get_existing_tests(output_dir)
    logger.info(f"Found {len(existing_tests)} existing tests")

    # Process each module
    tasks = []
    for module_path in modules:
        tasks.append(process_module(module_path, output_dir, existing_tests))

    # Wait for all modules to be processed
    results = await asyncio.gather(*tasks)

    # Flatten the list of results
    generated_files = [file for sublist in results for file in sublist]

    logger.info(f"Generated {len(generated_files)} test files")
    return generated_files

def save_test_generation_report(generated_files: List[str], output_dir: str) -> str:
    """
    Save a report of the test generation.

    Args:
        generated_files: List of paths to generated test files
        output_dir: The directory where tests were written

    Returns:
        Path to the report file
    """
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_files_generated": len(generated_files),
        "generated_files": generated_files,
        "output_directory": output_dir
    }

    report_file = Path(__file__).parent / "test_generation_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Saved test generation report to {report_file}")
    return str(report_file)

async def scheduled_test_generation(package_name: str, output_dir: str, interval_hours: float) -> None:
    """
    Run test generation on a schedule.

    Args:
        package_name: The name of the package to scan
        output_dir: The directory to write test files to
        interval_hours: How often to run the test generation (in hours)
    """
    interval_seconds = interval_hours * 3600

    while True:
        logger.info(f"Running scheduled test generation (interval: {interval_hours} hours)")

        try:
            # Generate tests
            generated_files = await generate_tests_for_package(package_name, output_dir)

            # Save report
            save_test_generation_report(generated_files, output_dir)

        except Exception as e:
            logger.error(f"Error during scheduled test generation: {e}")

        logger.info(f"Next test generation in {interval_hours} hours")
        await asyncio.sleep(interval_seconds)

async def async_main() -> None:
    """Asynchronous main function."""
    parser = argparse.ArgumentParser(description="Generate test stubs for untested functions")
    parser.add_argument("--package", default="augment_adam", help="The package to scan for untested functions")
    parser.add_argument("--module", help="Specific module to generate tests for (e.g., 'augment_adam.memory.faiss_memory')")
    parser.add_argument("--output-dir", default="tests/unit", help="The directory to write test files to")
    parser.add_argument("--schedule", type=float, help="Run on a schedule (interval in hours)")
    parser.add_argument("--report", action="store_true", help="Generate a report of test coverage")
    args = parser.parse_args()

    if args.schedule:
        # Run on a schedule
        await scheduled_test_generation(args.package, args.output_dir, args.schedule)
    elif args.module:
        # Process a specific module
        existing_tests = get_existing_tests(args.output_dir)
        generated_files = await process_module(args.module, args.output_dir, existing_tests)

        if args.report:
            save_test_generation_report(generated_files, args.output_dir)
    else:
        # Process the entire package
        generated_files = await generate_tests_for_package(args.package, args.output_dir)

        if args.report:
            save_test_generation_report(generated_files, args.output_dir)

def main():
    """Main function to generate test stubs."""
    # Run the async main function
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
