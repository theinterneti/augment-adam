#!/usr/bin/env python3
"""
Script to rename test files to avoid naming conflicts.
"""

import os
import shutil

# E2E test files
e2e_files = [
    ("tests/e2e/memory/core/test_base_e2e.py", "tests/e2e/memory/core/test_core_base_e2e.py"),
    ("tests/e2e/memory/episodic/test_base_e2e.py", "tests/e2e/memory/episodic/test_episodic_base_e2e.py"),
    ("tests/e2e/memory/graph/test_base_e2e.py", "tests/e2e/memory/graph/test_graph_base_e2e.py"),
    ("tests/e2e/memory/semantic/test_base_e2e.py", "tests/e2e/memory/semantic/test_semantic_base_e2e.py"),
    ("tests/e2e/memory/vector/test_base_e2e.py", "tests/e2e/memory/vector/test_vector_base_e2e.py"),
    ("tests/e2e/memory/working/test_base_e2e.py", "tests/e2e/memory/working/test_working_base_e2e.py"),
]

# Integration test files
integration_files = [
    ("tests/integration/memory/core/test_base_integration.py", "tests/integration/memory/core/test_core_base_integration.py"),
    ("tests/integration/memory/episodic/test_base_integration.py", "tests/integration/memory/episodic/test_episodic_base_integration.py"),
    ("tests/integration/memory/graph/test_base_integration.py", "tests/integration/memory/graph/test_graph_base_integration.py"),
    ("tests/integration/memory/semantic/test_base_integration.py", "tests/integration/memory/semantic/test_semantic_base_integration.py"),
    ("tests/integration/memory/vector/test_base_integration.py", "tests/integration/memory/vector/test_vector_base_integration.py"),
    ("tests/integration/memory/working/test_base_integration.py", "tests/integration/memory/working/test_working_base_integration.py"),
]

# Rename files
for old_path, new_path in e2e_files + integration_files:
    if os.path.exists(old_path):
        print(f"Renaming {old_path} to {new_path}")
        shutil.move(old_path, new_path)
    else:
        print(f"File not found: {old_path}")

print("Done!")
