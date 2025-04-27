#!/usr/bin/env python3
"""
Script to combine the testing framework documentation parts into a single file.
"""

import json
import os
from pathlib import Path

# Define the parts to combine
parts = [
    "docs/data/testing_framework_part1.json",
    "docs/data/testing_framework_part2.json",
    "docs/data/testing_framework_part3.json",
    "docs/data/testing_framework_part4.json",
    "docs/data/testing_framework_part5.json",
    "docs/data/testing_framework_part6.json"
]

# Load the first part (contains the title and description)
with open(parts[0], 'r') as f:
    combined_data = json.load(f)

# Initialize the sections list if it doesn't exist
if "sections" not in combined_data:
    combined_data["sections"] = []

# Load and combine the remaining parts
for part_file in parts[1:]:
    with open(part_file, 'r') as f:
        part_data = json.load(f)
        if "sections" in part_data:
            combined_data["sections"].extend(part_data["sections"])

# Save the combined data
output_path = Path("docs/data/testing_framework.json")
os.makedirs(output_path.parent, exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(combined_data, f, indent=2)

print(f"Combined testing framework documentation saved to {output_path}")

# Clean up the part files
for part_file in parts:
    os.remove(part_file)
    print(f"Removed {part_file}")

print("Done!")
