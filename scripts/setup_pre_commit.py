#!/usr/bin/env python
"""
Set up pre-commit hooks.

This script installs the pre-commit hooks defined in .pre-commit-config.yaml.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('setup-pre-commit')

def check_pre_commit_installed() -> bool:
    """
    Check if pre-commit is installed.
    
    Returns:
        True if pre-commit is installed, False otherwise.
    """
    try:
        subprocess.run(['pre-commit', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_pre_commit() -> bool:
    """
    Install pre-commit.
    
    Returns:
        True if pre-commit was installed successfully, False otherwise.
    """
    try:
        logger.info("Installing pre-commit...")
        subprocess.run(['pip', 'install', 'pre-commit'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing pre-commit: {e}")
        return False

def install_hooks() -> bool:
    """
    Install pre-commit hooks.
    
    Returns:
        True if hooks were installed successfully, False otherwise.
    """
    try:
        logger.info("Installing pre-commit hooks...")
        subprocess.run(['pre-commit', 'install'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing pre-commit hooks: {e}")
        return False

def main() -> int:
    """
    Main function.
    
    Returns:
        0 if successful, 1 otherwise.
    """
    # Check if pre-commit is installed
    if not check_pre_commit_installed():
        logger.info("pre-commit is not installed.")
        if not install_pre_commit():
            logger.error("Failed to install pre-commit.")
            return 1
    
    # Install hooks
    if not install_hooks():
        logger.error("Failed to install pre-commit hooks.")
        return 1
    
    logger.info("Pre-commit hooks installed successfully!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
