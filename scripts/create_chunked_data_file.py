#!/usr/bin/env python3
"""
Script to create documentation data files in smaller chunks.

This script takes a JSON data structure and saves it to a file in smaller chunks
to avoid hitting API limits.
"""

import json
import os
import sys
from pathlib import Path
import argparse

def save_json_in_chunks(data, output_path, chunk_size=5000):
    """
    Save a JSON data structure to a file in smaller chunks.
    
    Args:
        data: The JSON data structure to save.
        output_path: The path to save the file to.
        chunk_size: The maximum size of each chunk in characters.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert the data to a JSON string
    json_str = json.dumps(data, indent=2)
    
    # Split the JSON string into chunks
    chunks = []
    current_chunk = ""
    for line in json_str.split("\n"):
        if len(current_chunk) + len(line) + 1 > chunk_size:
            chunks.append(current_chunk)
            current_chunk = line
        else:
            if current_chunk:
                current_chunk += "\n" + line
            else:
                current_chunk = line
    
    if current_chunk:
        chunks.append(current_chunk)
    
    # Save the chunks to the file
    with open(output_path, "w") as f:
        for i, chunk in enumerate(chunks):
            print(f"Writing chunk {i+1}/{len(chunks)} ({len(chunk)} characters)")
            f.write(chunk)
            if i < len(chunks) - 1:
                f.write("\n")
    
    print(f"Saved {len(json_str)} characters in {len(chunks)} chunks to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Create documentation data files in smaller chunks.")
    parser.add_argument("input_file", help="Input JSON file to process")
    parser.add_argument("output_file", help="Output file to save")
    parser.add_argument("--chunk-size", type=int, default=5000, help="Maximum size of each chunk in characters")
    
    args = parser.parse_args()
    
    # Load the input data
    with open(args.input_file, "r") as f:
        data = json.load(f)
    
    # Save the data in chunks
    save_json_in_chunks(data, args.output_file, args.chunk_size)

if __name__ == "__main__":
    main()
