#!/usr/bin/env python
"""
Set up Git commit message template.

This script sets up the Git commit message template for the project.
It configures Git to use the .gitmessage file as the commit template.
"""

import os
import subprocess
import sys


def setup_git_commit_template():
    """
    Set up the Git commit message template.

    Returns:
        0 if successful, 1 otherwise.
    """
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(project_root, ".gitmessage")

        # Check if the template file exists
        if not os.path.exists(template_path):
            print(f"Error: Commit message template file not found at {template_path}")
            return 1

        # Set the commit template
        subprocess.run(
            ["git", "config", "--local", "commit.template", ".gitmessage"],
            check=True,
        )

        print("Git commit message template set up successfully.")
        print("You can now use 'git commit' without -m to use the template.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error setting up Git commit message template: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(setup_git_commit_template())
