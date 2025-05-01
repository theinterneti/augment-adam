#!/usr/bin/env python3
"""
Test script to verify connectivity to all services in the Docker environment.
"""

import os
import sys
import time
import requests
import redis
from neo4j import GraphDatabase

def test_ollama():
    """Test connection to Ollama service."""
    print("\nTesting Ollama service...")
    try:
        response = requests.get("http://ollama:11434/api/tags")
        if response.status_code == 200:
            print("✅ Ollama service is accessible")
            print(f"Available models: {response.json()}")
            return True
        else:
            print(f"❌ Ollama service returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama service: {str(e)}")
        return False

def test_chroma():
    """Test connection to ChromaDB service."""
    print("\nTesting ChromaDB service...")
    try:
        response = requests.get("http://chroma:8000/api/v2/heartbeat")
        if response.status_code == 200:
            print("✅ ChromaDB service is accessible")
            print(f"Heartbeat: {response.json()}")
            return True
        else:
            print(f"❌ ChromaDB service returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to ChromaDB service: {str(e)}")
        return False

def test_neo4j():
    """Test connection to Neo4j service."""
    print("\nTesting Neo4j service...")
    try:
        uri = "bolt://neo4j:7687"
        user = "neo4j"
        password = "augmentpassword"
        
        with GraphDatabase.driver(uri, auth=(user, password)) as driver:
            with driver.session() as session:
                result = session.run("RETURN 'Neo4j connection successful' AS message")
                message = result.single()["message"]
                print(f"✅ {message}")
                return True
    except Exception as e:
        print(f"❌ Error connecting to Neo4j service: {str(e)}")
        return False

def test_redis():
    """Test connection to Redis service."""
    print("\nTesting Redis service...")
    try:
        r = redis.Redis(host='redis', port=6379)
        if r.ping():
            print("✅ Redis service is accessible")
            return True
        else:
            print("❌ Redis service ping failed")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Redis service: {str(e)}")
        return False

def test_redis_vector():
    """Test connection to Redis Vector service."""
    print("\nTesting Redis Vector service...")
    try:
        r = redis.Redis(host='redis-vector', port=6379, password='redispassword')
        if r.ping():
            print("✅ Redis Vector service is accessible")
            # Try to create a simple index
            try:
                r.execute_command(
                    'FT.CREATE', 'idx:test', 'ON', 'HASH', 'PREFIX', '1', 'test:', 
                    'SCHEMA', 'txt', 'TEXT'
                )
                print("✅ Redis Vector service index creation successful")
            except redis.exceptions.ResponseError as e:
                if "Index already exists" in str(e):
                    print("✅ Redis Vector service index already exists")
                else:
                    print(f"⚠️ Redis Vector service index creation error: {str(e)}")
            return True
        else:
            print("❌ Redis Vector service ping failed")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Redis Vector service: {str(e)}")
        return False

def main():
    """Main function to run all tests."""
    print("Testing Docker services connectivity")
    print("===================================")
    
    # Run all tests
    ollama_ok = test_ollama()
    chroma_ok = test_chroma()
    neo4j_ok = test_neo4j()
    redis_ok = test_redis()
    redis_vector_ok = test_redis_vector()
    
    # Print summary
    print("\nSummary:")
    print(f"Ollama: {'✅' if ollama_ok else '❌'}")
    print(f"ChromaDB: {'✅' if chroma_ok else '❌'}")
    print(f"Neo4j: {'✅' if neo4j_ok else '❌'}")
    print(f"Redis: {'✅' if redis_ok else '❌'}")
    print(f"Redis Vector: {'✅' if redis_vector_ok else '❌'}")
    
    # Return success if all tests passed
    if all([ollama_ok, chroma_ok, neo4j_ok, redis_ok, redis_vector_ok]):
        print("\n✅ All services are accessible and working correctly!")
        return 0
    else:
        print("\n❌ Some services are not accessible or not working correctly.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
