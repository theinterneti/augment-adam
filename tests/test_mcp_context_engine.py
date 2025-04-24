#!/usr/bin/env python3

import requests
import json
import time
import argparse
import sys

# Default API URL
API_URL = "http://localhost:8080"
API_KEY = "test-api-key"

def test_health():
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{API_URL}/api/health", headers={"X-API-Key": API_KEY})
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_vector_store():
    """Test the vector_store endpoint."""
    try:
        # Store a test vector
        data = {
            "text": "def hello_world():\n    print('Hello, world!')",
            "metadata": {
                "file_path": "test.py",
                "language": "python",
                "created_at": int(time.time())
            },
            "tier": "hot"
        }
        
        response = requests.post(f"{API_URL}/api/vector/store", json=data, headers={"X-API-Key": API_KEY})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Vector store test passed: {result['vector_id']}")
            return result["vector_id"]
        else:
            print(f"❌ Vector store test failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return None

def test_vector_search():
    """Test the vector_search endpoint."""
    try:
        # Wait for the vector to be indexed
        time.sleep(2)
        
        # Search for the test vector
        data = {
            "query": "function that prints hello world",
            "k": 10,
            "include_metadata": True
        }
        
        response = requests.post(f"{API_URL}/api/vector/search", json=data, headers={"X-API-Key": API_KEY})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Vector search test passed: {len(result['results'])} results found")
            print(f"   Query time: {result['query_time_ms']:.2f} ms")
            
            if result["results"]:
                top_result = result["results"][0]
                print(f"   Top result: {top_result['id']} (score: {top_result['score']:.4f})")
                print(f"   Metadata: {json.dumps(top_result['metadata'], indent=2)}")
            
            return True
        else:
            print(f"❌ Vector search test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Vector search test failed: {e}")
        return False

def test_code_index():
    """Test the code_index endpoint."""
    try:
        # Index a test code snippet
        data = {
            "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
            "file_path": "factorial.py",
            "language": "python",
            "tier": "hot"
        }
        
        response = requests.post(f"{API_URL}/api/code/index", json=data, headers={"X-API-Key": API_KEY})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Code index test passed: {result['vector_id']}")
            return result["vector_id"]
        else:
            print(f"❌ Code index test failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Code index test failed: {e}")
        return None

def test_create_relationship():
    """Test the create_relationship endpoint."""
    try:
        # Create a relationship between two vectors
        vector_id1 = test_vector_store()
        vector_id2 = test_code_index()
        
        if not vector_id1 or not vector_id2:
            print("❌ Create relationship test failed: Missing vector IDs")
            return False
        
        data = {
            "from_id": vector_id1,
            "to_id": vector_id2,
            "relationship_type": "RELATED_TO",
            "properties": {
                "weight": 0.8,
                "created_at": int(time.time())
            }
        }
        
        response = requests.post(f"{API_URL}/api/graph/relationship", json=data, headers={"X-API-Key": API_KEY})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Create relationship test passed: {result['status']}")
            print(f"   Message: {result['message']}")
            return True
        else:
            print(f"❌ Create relationship test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Create relationship test failed: {e}")
        return False

def test_get_related_vectors():
    """Test the get_related_vectors endpoint."""
    try:
        # Create vectors and relationship first
        vector_id1 = test_vector_store()
        vector_id2 = test_code_index()
        
        if not vector_id1 or not vector_id2:
            print("❌ Get related vectors test failed: Missing vector IDs")
            return False
        
        # Create relationship
        data = {
            "from_id": vector_id1,
            "to_id": vector_id2,
            "relationship_type": "RELATED_TO"
        }
        
        response = requests.post(f"{API_URL}/api/graph/relationship", json=data, headers={"X-API-Key": API_KEY})
        
        if response.status_code != 200:
            print(f"❌ Get related vectors test failed: Could not create relationship")
            return False
        
        # Wait for the relationship to be created
        time.sleep(2)
        
        # Get related vectors
        data = {
            "vector_id": vector_id1,
            "relationship_type": "RELATED_TO",
            "max_depth": 1
        }
        
        response = requests.post(f"{API_URL}/api/graph/related", json=data, headers={"X-API-Key": API_KEY})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Get related vectors test passed: {len(result['vectors'])} vectors found")
            
            if result["vectors"]:
                related_vector = result["vectors"][0]
                print(f"   Related vector: {related_vector['id']}")
                print(f"   Metadata: {json.dumps(related_vector['metadata'], indent=2)}")
            
            return True
        else:
            print(f"❌ Get related vectors test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get related vectors test failed: {e}")
        return False

def test_mcp_tools():
    """Test the MCP tools endpoint."""
    try:
        response = requests.get(f"{API_URL}/mcp/tools")
        if response.status_code == 200:
            tools = response.json()
            print(f"✅ MCP tools check passed: {len(tools)} tools available")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
            return True
        else:
            print(f"❌ MCP tools check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP tools check failed: {e}")
        return False

def test_mcp_connection():
    """Test the MCP connection endpoint."""
    try:
        response = requests.get(f"{API_URL}/mcp/connection")
        if response.status_code == 200:
            print(f"✅ MCP connection check passed")
            return True
        else:
            print(f"❌ MCP connection check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP connection check failed: {e}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test the MCP-enabled context engine")
    parser.add_argument("--url", default=API_URL, help="API URL")
    parser.add_argument("--key", default=API_KEY, help="API key")
    parser.add_argument("--test", choices=["all", "health", "store", "search", "code", "relationship", "related", "mcp-tools", "mcp-connection"], default="all", help="Test to run")
    
    args = parser.parse_args()
    
    global API_URL, API_KEY
    API_URL = args.url
    API_KEY = args.key
    
    print(f"Testing MCP-enabled context engine at {API_URL}")
    
    if args.test == "all" or args.test == "health":
        if not test_health():
            sys.exit(1)
    
    if args.test == "all" or args.test == "store":
        if not test_vector_store():
            sys.exit(1)
    
    if args.test == "all" or args.test == "search":
        if not test_vector_search():
            sys.exit(1)
    
    if args.test == "all" or args.test == "code":
        if not test_code_index():
            sys.exit(1)
    
    if args.test == "all" or args.test == "relationship":
        if not test_create_relationship():
            sys.exit(1)
    
    if args.test == "all" or args.test == "related":
        if not test_get_related_vectors():
            sys.exit(1)
    
    if args.test == "all" or args.test == "mcp-tools":
        if not test_mcp_tools():
            sys.exit(1)
    
    if args.test == "all" or args.test == "mcp-connection":
        if not test_mcp_connection():
            sys.exit(1)
    
    print("All tests passed!")

if __name__ == "__main__":
    main()
