#!/usr/bin/env python3

"""Client library for the context engine."""

import json
import time
from typing import Dict, Any, List, Optional
import requests

class ContextEngineClient:
    """Client for the context engine."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """Initialize the client.
        
        Args:
            base_url: Base URL of the context engine API
        """
        self.base_url = base_url
    
    def health(self) -> Dict[str, Any]:
        """Check the health of the context engine.
        
        Returns:
            Health status
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get the available MCP tools.
        
        Returns:
            List of available tools
        """
        response = requests.get(f"{self.base_url}/mcp/tools")
        response.raise_for_status()
        return response.json()
    
    def vector_search(self, query: str, k: int = 10, include_metadata: bool = True, 
                     filter_dict: Optional[Dict[str, Any]] = None, use_graph: bool = False) -> Dict[str, Any]:
        """Search for vectors similar to the query.
        
        Args:
            query: Query text
            k: Number of results to return
            include_metadata: Whether to include metadata in the results
            filter_dict: Filter to apply to the results
            use_graph: Whether to use graph search (Neo4j) instead of vector search (Redis)
            
        Returns:
            Search results
        """
        data = {
            "name": "vector_search",
            "parameters": {
                "query": query,
                "k": k,
                "include_metadata": include_metadata,
                "filter": filter_dict,
                "use_graph": use_graph
            }
        }
        
        response = requests.post(f"{self.base_url}/mcp/tools", json=data)
        response.raise_for_status()
        return response.json()
    
    def vector_store(self, text: str, metadata: Dict[str, Any], tier: str = "hot", 
                    vector_id: Optional[str] = None) -> Dict[str, Any]:
        """Store a vector in the database.
        
        Args:
            text: Text to encode and store
            metadata: Metadata for the vector
            tier: Storage tier (hot, warm, or cold)
            vector_id: Custom vector ID (generated if not provided)
            
        Returns:
            Status of the operation
        """
        data = {
            "name": "vector_store",
            "parameters": {
                "text": text,
                "metadata": metadata,
                "tier": tier,
                "vector_id": vector_id
            }
        }
        
        response = requests.post(f"{self.base_url}/mcp/tools", json=data)
        response.raise_for_status()
        return response.json()
    
    def code_index(self, code: str, file_path: str, language: Optional[str] = None, 
                  tier: str = "hot", additional_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Index code in the database.
        
        Args:
            code: Code to index
            file_path: Path to the file
            language: Programming language (detected from file extension if not provided)
            tier: Storage tier (hot, warm, or cold)
            additional_metadata: Additional metadata
            
        Returns:
            Status of the operation
        """
        data = {
            "name": "code_index",
            "parameters": {
                "code": code,
                "file_path": file_path,
                "language": language,
                "tier": tier,
                "additional_metadata": additional_metadata
            }
        }
        
        response = requests.post(f"{self.base_url}/mcp/tools", json=data)
        response.raise_for_status()
        return response.json()
    
    def create_relationship(self, from_id: str, to_id: str, relationship_type: str, 
                           properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a relationship between two vectors.
        
        Args:
            from_id: Source vector ID
            to_id: Target vector ID
            relationship_type: Type of relationship
            properties: Relationship properties
            
        Returns:
            Status of the operation
        """
        data = {
            "name": "create_relationship",
            "parameters": {
                "from_id": from_id,
                "to_id": to_id,
                "relationship_type": relationship_type,
                "properties": properties
            }
        }
        
        response = requests.post(f"{self.base_url}/mcp/tools", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_related_vectors(self, vector_id: str, relationship_type: Optional[str] = None, 
                           max_depth: int = 1) -> Dict[str, Any]:
        """Get vectors related to a vector.
        
        Args:
            vector_id: Vector ID
            relationship_type: Type of relationship (None for any)
            max_depth: Maximum depth of relationships
            
        Returns:
            Related vectors
        """
        data = {
            "name": "get_related_vectors",
            "parameters": {
                "vector_id": vector_id,
                "relationship_type": relationship_type,
                "max_depth": max_depth
            }
        }
        
        response = requests.post(f"{self.base_url}/mcp/tools", json=data)
        response.raise_for_status()
        return response.json()
    
    def index_repository(self, repo_path: str, file_extensions: Optional[List[str]] = None, 
                        tier: str = "hot", max_workers: int = 4) -> Dict[str, Any]:
        """Index a repository.
        
        Args:
            repo_path: Path to the repository
            file_extensions: File extensions to index (None for all supported extensions)
            tier: Storage tier (hot, warm, or cold)
            max_workers: Maximum number of worker threads
            
        Returns:
            Status of the operation
        """
        import os
        from concurrent.futures import ThreadPoolExecutor
        from pathlib import Path
        
        # Supported file extensions
        supported_extensions = file_extensions or [
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
            ".c", ".cpp", ".h", ".hpp", ".rb", ".php", ".cs", ".swift",
            ".kt", ".scala", ".sh", ".md", ".json", ".yaml", ".yml",
            ".toml", ".xml", ".html", ".css", ".scss", ".sql", ".graphql", ".proto"
        ]
        
        # Directories to ignore
        ignore_dirs = [
            ".git", "node_modules", "venv", "env", "__pycache__",
            "dist", "build", "target", ".idea", ".vscode"
        ]
        
        # Find all files
        repo_path = Path(repo_path).resolve()
        files_to_index = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                
                # Skip files without recognized extensions
                if ext not in supported_extensions:
                    continue
                
                files_to_index.append(file_path)
        
        print(f"Found {len(files_to_index)} files to index")
        
        # Index files in parallel
        indexed_count = 0
        failed_count = 0
        
        def index_file(file_path):
            try:
                # Read the file
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Skip empty files
                if not content.strip():
                    print(f"Skipping empty file: {file_path}")
                    return False
                
                # Index the file
                result = self.code_index(
                    code=content,
                    file_path=str(file_path),
                    tier=tier
                )
                
                print(f"Indexed file: {file_path} (vector_id: {result['vector_id']})")
                return True
            
            except Exception as e:
                print(f"Error indexing file: {file_path} ({e})")
                return False
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(index_file, files_to_index))
        
        # Print summary
        indexed_count = sum(1 for r in results if r)
        failed_count = sum(1 for r in results if not r)
        
        return {
            "indexed_count": indexed_count,
            "failed_count": failed_count,
            "total_count": len(files_to_index)
        }


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Context Engine Client")
    parser.add_argument("--url", default="http://localhost:8080", help="API URL")
    parser.add_argument("command", choices=["health", "tools", "search", "store", "index", "repository"], help="Command to run")
    parser.add_argument("--query", help="Query text for search")
    parser.add_argument("--text", help="Text to store")
    parser.add_argument("--file", help="File to index")
    parser.add_argument("--repo", help="Repository to index")
    parser.add_argument("--tier", default="hot", choices=["hot", "warm", "cold"], help="Storage tier")
    
    args = parser.parse_args()
    
    client = ContextEngineClient(args.url)
    
    if args.command == "health":
        result = client.health()
        print(json.dumps(result, indent=2))
    
    elif args.command == "tools":
        result = client.get_tools()
        print(json.dumps(result, indent=2))
    
    elif args.command == "search":
        if not args.query:
            print("Error: --query is required for search")
            exit(1)
        
        result = client.vector_search(args.query)
        print(json.dumps(result, indent=2))
    
    elif args.command == "store":
        if not args.text:
            print("Error: --text is required for store")
            exit(1)
        
        result = client.vector_store(
            text=args.text,
            metadata={"source": "command_line", "created_at": int(time.time())},
            tier=args.tier
        )
        print(json.dumps(result, indent=2))
    
    elif args.command == "index":
        if not args.file:
            print("Error: --file is required for index")
            exit(1)
        
        with open(args.file, "r") as f:
            code = f.read()
        
        result = client.code_index(
            code=code,
            file_path=args.file,
            tier=args.tier
        )
        print(json.dumps(result, indent=2))
    
    elif args.command == "repository":
        if not args.repo:
            print("Error: --repo is required for repository")
            exit(1)
        
        result = client.index_repository(
            repo_path=args.repo,
            tier=args.tier
        )
        print(json.dumps(result, indent=2))
