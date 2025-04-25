#!/usr/bin/env python3

import os
import argparse
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import mimetypes

# Default API URL
API_URL = "http://localhost:8080"

# File extensions to index
CODE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".sh": "bash",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".sql": "sql",
    ".graphql": "graphql",
    ".proto": "protobuf"
}

# Directories to ignore
IGNORE_DIRS = [
    ".git",
    "node_modules",
    "venv",
    "env",
    "__pycache__",
    "dist",
    "build",
    "target",
    ".idea",
    ".vscode"
]

def is_binary_file(file_path):
    """Check if a file is binary."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        return True
    return not mime_type.startswith("text/")

def index_file(file_path, api_url):
    """Index a single file."""
    try:
        # Skip binary files
        if is_binary_file(file_path):
            print(f"Skipping binary file: {file_path}")
            return False
        
        # Read the file
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Skip empty files
        if not content.strip():
            print(f"Skipping empty file: {file_path}")
            return False
        
        # Get the file extension
        ext = os.path.splitext(file_path)[1].lower()
        language = CODE_EXTENSIONS.get(ext, "text")
        
        # Create metadata
        metadata = {
            "file_path": str(file_path),
            "language": language,
            "created_at": int(time.time()),
            "size": len(content)
        }
        
        # Store the vector
        data = {
            "text": content,
            "metadata": metadata,
            "tier": "hot"
        }
        
        response = requests.post(f"{api_url}/store", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Indexed file: {file_path} (task_id: {result['task_id']})")
            return True
        else:
            print(f"Failed to index file: {file_path} ({response.status_code})")
            return False
    
    except Exception as e:
        print(f"Error indexing file: {file_path} ({e})")
        return False

def index_repository(repo_path, api_url, max_workers=4):
    """Index a repository."""
    repo_path = Path(repo_path).resolve()
    
    if not repo_path.exists():
        print(f"Repository path does not exist: {repo_path}")
        return False
    
    print(f"Indexing repository: {repo_path}")
    
    # Find all files
    files_to_index = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            file_path = Path(root) / file
            ext = file_path.suffix.lower()
            
            # Skip files without recognized extensions
            if ext not in CODE_EXTENSIONS:
                continue
            
            files_to_index.append(file_path)
    
    print(f"Found {len(files_to_index)} files to index")
    
    # Index files in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(lambda f: index_file(f, api_url), files_to_index))
    
    # Print summary
    indexed_count = sum(1 for r in results if r)
    failed_count = sum(1 for r in results if not r)
    
    print(f"Indexing complete:")
    print(f"  - Indexed: {indexed_count}")
    print(f"  - Failed: {failed_count}")
    
    return indexed_count > 0

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Index a repository in the context engine")
    parser.add_argument("repo_path", help="Path to the repository")
    parser.add_argument("--url", default=API_URL, help="API URL")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker threads")
    
    args = parser.parse_args()
    
    index_repository(args.repo_path, args.url, args.workers)

if __name__ == "__main__":
    main()
