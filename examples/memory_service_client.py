#!/usr/bin/env python3
"""
Memory Service Client Example

This script demonstrates how to use the Memory Service API from Python.
"""

import requests
import json
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class MemoryServiceClient:
    """Client for the Memory Service API."""
    
    def __init__(self, base_url: str):
        """Initialize the client.
        
        Args:
            base_url: Base URL of the Memory Service API
        """
        self.base_url = base_url
        self.session = requests.Session()
    
    def add_memory(self, text: str, metadata: dict = None) -> dict:
        """Add a new memory.
        
        Args:
            text: Text content of the memory
            metadata: Additional metadata for the memory
        
        Returns:
            The created memory with ID
        """
        url = f"{self.base_url}/memories"
        data = {"text": text, "metadata": metadata or {}}
        
        response = self.session.post(url, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_memory(self, memory_id: str) -> dict:
        """Get a memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
        
        Returns:
            The memory with the specified ID
        """
        url = f"{self.base_url}/memories/{memory_id}"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def list_memories(self) -> dict:
        """List all memories.
        
        Returns:
            List of all memories
        """
        url = f"{self.base_url}/memories"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def delete_memory(self, memory_id: str) -> dict:
        """Delete a memory by ID.
        
        Args:
            memory_id: ID of the memory to delete
        
        Returns:
            Success message
        """
        url = f"{self.base_url}/memories/{memory_id}"
        
        response = self.session.delete(url)
        response.raise_for_status()
        
        return response.json()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Memory Service Client Example")
    parser.add_argument("--url", default="http://localhost:8811", help="Base URL of the Memory Service API")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create client
    client = MemoryServiceClient(args.url)
    
    # Add a memory
    logger.info("Adding a memory...")
    result = client.add_memory(
        text="This is a memory from the Python client",
        metadata={"source": "python_client", "importance": 0.9}
    )
    memory_id = result["memory"]["id"]
    logger.info(f"Added memory with ID: {memory_id}")
    
    # Get the memory
    logger.info(f"Getting memory with ID: {memory_id}...")
    result = client.get_memory(memory_id)
    logger.info(f"Memory: {json.dumps(result, indent=2)}")
    
    # List all memories
    logger.info("Listing all memories...")
    result = client.list_memories()
    logger.info(f"Memories: {json.dumps(result, indent=2)}")
    
    # Delete the memory
    logger.info(f"Deleting memory with ID: {memory_id}...")
    result = client.delete_memory(memory_id)
    logger.info(f"Result: {json.dumps(result, indent=2)}")
    
    # List all memories again
    logger.info("Listing all memories after deletion...")
    result = client.list_memories()
    logger.info(f"Memories: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    main()
