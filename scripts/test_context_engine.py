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

def test_store():
    """Test the store endpoint."""
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
        
        response = requests.post(f"{API_URL}/store", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Store test passed: {result['task_id']}")
            return result["task_id"]
        else:
            print(f"❌ Store test failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Store test failed: {e}")
        return None

def test_search():
    """Test the search endpoint."""
    try:
        # Wait for the vector to be indexed
        time.sleep(2)
        
        # Search for the test vector
        data = {
            "query": "function that prints hello world",
            "k": 10,
            "include_metadata": True
        }
        
        response = requests.post(f"{API_URL}/search", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Search test passed: {len(result['results'])} results found")
            print(f"   Query time: {result['query_time_ms']:.2f} ms")
            
            if result["results"]:
                top_result = result["results"][0]
                print(f"   Top result: {top_result['id']} (score: {top_result['score']:.4f})")
                print(f"   Metadata: {json.dumps(top_result['metadata'], indent=2)}")
            
            return True
        else:
            print(f"❌ Search test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def test_graph_search():
    """Test the graph search endpoint."""
    try:
        # Wait for the vector to be indexed
        time.sleep(2)
        
        # Search for the test vector
        data = {
            "query": "function that prints hello world",
            "k": 10,
            "filter": {"language": "python"}
        }
        
        response = requests.post(f"{API_URL}/graph-search", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Graph search test passed: {len(result['results'])} results found")
            
            if result["results"]:
                top_result = result["results"][0]
                print(f"   Top result: {top_result['id']} (score: {top_result['score']:.4f})")
                print(f"   Metadata: {json.dumps(top_result['metadata'], indent=2)}")
            
            return True
        else:
            print(f"❌ Graph search test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Graph search test failed: {e}")
        return False

def test_performance():
    """Test the performance of the search endpoint."""
    try:
        # Number of queries to run
        num_queries = 100
        
        # Search query
        data = {
            "query": "function that prints hello world",
            "k": 10,
            "include_metadata": True
        }
        
        # Run the queries
        start_time = time.time()
        
        for i in range(num_queries):
            response = requests.post(f"{API_URL}/search", json=data)
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
    parser.add_argument("--test", choices=["all", "health", "store", "search", "graph-search", "performance"], default="all", help="Test to run")
    
    args = parser.parse_args()
    
    global API_URL
    API_URL = args.url
    
    print(f"Testing context engine API at {API_URL}")
    
    if args.test == "all" or args.test == "health":
        if not test_health():
            sys.exit(1)
    
    if args.test == "all" or args.test == "store":
        task_id = test_store()
        if not task_id:
            sys.exit(1)
    
    if args.test == "all" or args.test == "search":
        if not test_search():
            sys.exit(1)
    
    if args.test == "all" or args.test == "graph-search":
        if not test_graph_search():
            sys.exit(1)
    
    if args.test == "all" or args.test == "performance":
        if not test_performance():
            sys.exit(1)
    
    print("All tests passed!")

if __name__ == "__main__":
    main()
