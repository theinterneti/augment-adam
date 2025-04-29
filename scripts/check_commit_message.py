#!/usr/bin/env python
"""
Check commit message format.

This script checks that commit messages follow the conventional commits format:
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, test, chore
Scope: optional, describes the section of the codebase
Subject: short description of the change
"""

import re
import sys


def check_commit_message(filename):
    """
    Check that the commit message follows the conventional commits format.

    Args:
        filename: Path to the file containing the commit message.

    Returns:
        0 if the message is valid, 1 otherwise.
    """
    with open(filename, "r") as f:
        message = f.read()

    # Get the first line (subject)
    subject = message.split("\n")[0].strip()

    # Define the pattern for conventional commits
    pattern = r"^(feat|fix|docs|style|refactor|test|chore)(\([a-z0-9-]+\))?: .{1,50}$"

    # Check if the subject matches the pattern
    if not re.match(pattern, subject):
        print("Error: Commit message does not follow the conventional commits format.")
        print("Format: <type>(<scope>): <subject>")
        print("Types: feat, fix, docs, style, refactor, test, chore")
        print("Example: feat(memory): add Redis-based vector storage")
        return 1

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_commit_message.py <commit-message-file>")
        sys.exit(1)

    sys.exit(check_commit_message(sys.argv[1]))
