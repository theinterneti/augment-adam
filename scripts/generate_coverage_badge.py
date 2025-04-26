#!/usr/bin/env python
"""
Generate a coverage badge.

This script generates a coverage badge based on the coverage report.
"""

import os
import sys
import subprocess
import logging
import xml.etree.ElementTree as ET
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('generate-coverage-badge')

def get_coverage_from_xml() -> float:
    """
    Get the coverage percentage from the coverage XML report.
    
    Returns:
        The coverage percentage as a float.
    """
    try:
        tree = ET.parse('coverage.xml')
        root = tree.getroot()
        coverage = float(root.attrib['line-rate']) * 100
        return coverage
    except (ET.ParseError, KeyError, FileNotFoundError) as e:
        logger.error(f"Error parsing coverage.xml: {e}")
        return 0.0

def generate_badge(coverage: float) -> None:
    """
    Generate a coverage badge.
    
    Args:
        coverage: The coverage percentage.
    """
    try:
        # Determine the color based on coverage
        if coverage >= 90:
            color = 'brightgreen'
        elif coverage >= 80:
            color = 'green'
        elif coverage >= 70:
            color = 'yellowgreen'
        elif coverage >= 60:
            color = 'yellow'
        elif coverage >= 50:
            color = 'orange'
        else:
            color = 'red'
        
        # Create the badge URL
        badge_url = f"https://img.shields.io/badge/coverage-{coverage:.1f}%25-{color}"
        
        # Create the badge markdown
        badge_markdown = f"![Coverage]({badge_url})"
        
        # Save the badge markdown to a file
        with open('coverage-badge.md', 'w') as f:
            f.write(badge_markdown)
        
        logger.info(f"Generated coverage badge: {badge_markdown}")
    except Exception as e:
        logger.error(f"Error generating badge: {e}")

def main() -> int:
    """
    Main function.
    
    Returns:
        0 if successful, 1 otherwise.
    """
    # Get the coverage percentage
    coverage = get_coverage_from_xml()
    
    if coverage == 0.0:
        logger.error("Failed to get coverage percentage.")
        return 1
    
    # Generate the badge
    generate_badge(coverage)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
