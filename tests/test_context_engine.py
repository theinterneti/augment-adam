#!/usr/bin/env python3

import requests
import json
import time
import argparse
import sys

# Default API URL
API_URL = "http://localhost:8080"

def test_health():
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_mcp_tools():
    """Test the MCP tools."""
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

def test_vector_store():
    """Test the vector_store tool."""
    try:
        # Store a test vector
        data = {
            "name": "vector_store",
            "parameters": {
                "text": "def hello_world():\n    print('Hello, world!')",
                "metadata": {
                    "file_path": "test.py",
                    "language": "python",
                    "created_at": int(time.time())
                },
                "tier": "hot"
            }
        }
        
        response = requests.post(f"{API_URL}/mcp/tools", json=data)
        
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
    """Test the vector_search tool."""
    try:
        # Wait for the vector to be indexed
        time.sleep(2)
        
        # Search for the test vector
        data = {
            "name": "vector_search",
            "parameters": {
                "query": "function that prints hello world",
                "k": 10,
                "include_metadata": True
            }
        }
        
        response = requests.post(f"{API_URL}/mcp/tools", json=data)
        
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
    """Test the code_index tool."""
    try:
        # Index a test code snippet
        data = {
            "name": "code_index",
            "parameters": {
                "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
                "file_path": "factorial.py",
                "language": "python",
                "tier": "hot"
            }
        }
        
        response = requests.post(f"{API_URL}/mcp/tools", json=data)
        
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
    """Test the create_relationship tool."""
    try:
        # Create a relationship between two vectors
        vector_id1 = test_vector_store()
        vector_id2 = test_code_index()
        
        if not vector_id1 or not vector_id2:
            print("❌ Create relationship test failed: Missing vector IDs")
            return False
        
        data = {
            "name": "create_relationship",
            "parameters": {
                "from_id": vector_id1,
                "to_id": vector_id2,
                "relationship_type": "RELATED_TO",
                "properties": {
                    "weight": 0.8,
                    "created_at": int(time.time())
                }
            }
        }
        
        response = requests.post(f"{API_URL}/mcp/tools", json=data)
        
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
    """Test the get_related_vectors tool."""
    try:
        # Create vectors and relationship first
        vector_id1 = test_vector_store()
        vector_id2 = test_code_index()
        
        if not vector_id1 or not vector_id2:
            print("❌ Get related vectors test failed: Missing vector IDs")
            return False
        
        # Create relationship
        data = {
            "name": "create_relationship",
            "parameters": {
                "from_id": vector_id1,
                "to_id": vector_id2,
                "relationship_type": "RELATED_TO"
            }
        }
        
        response = requests.post(f"{API_URL}/mcp/tools", json=data)
        
        if response.status_code != 200:
            print(f"❌ Get related vectors test failed: Could not create relationship")
            return False
        
        # Wait for the relationship to be created
        time.sleep(2)
        
        # Get related vectors
        data = {
            "name": "get_related_vectors",
            "parameters": {
                "vector_id": vector_id1,
                "relationship_type": "RELATED_TO",
                "max_depth": 1
            }
        }
        
        response = requests.post(f"{API_URL}/mcp/tools", json=data)
        
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

def test_performance():
    """Test the performance of the vector_search tool."""
    try:
        # Number of queries to run
        num_queries = 100
        
        # Search query
        data = {
            "name": "vector_search",
            "parameters": {
                "query": "function that prints hello world",
                "k": 10,
                "include_metadata": True
            }
        }
        
        # Run the queries
        start_time = time.time()
        
        for i in range(num_queries):
            response = requests.post(f"{API_URL}/mcp/tools", json=data)
            if response.status_code != 200:
                print(f"❌ Performance test failed on query {i}: {response.status_code}")
                return False
        
        end_time = time.time()
        
        # Calculate the results
        total_time = end_time - start_time
        avg_time = total_time / num_queries
        qps = num_queries / total_time
        
        print(f"✅ Performance test passed:")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Average time per query: {avg_time * 1000:.2f} ms")
        print(f"   Queries per second: {qps:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test the context engine API")
    parser.add_argument("--url", default=API_URL, help="API URL")
    parser.add_argument("--test", choices=["all", "health", "mcp", "store", "search", "code", "relationship", "related", "performance"], default="all", help="Test to run")
    
    args = parser.parse_args()
    
    global API_URL
    API_URL = args.url
    
    print(f"Testing context engine API at {API_URL}")
    
    if args.test == "all" or args.test == "health":
        if not test_health():
            sys.exit(1)
    
    if args.test == "all" or args.test == "mcp":
        if not test_mcp_tools():
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
    
    if args.test == "all" or args.test == "performance":
        if not test_performance():
            sys.exit(1)
    
    print("All tests passed!")

if __name__ == "__main__":
    main()
