#!/usr/bin/env python
"""
Advanced Memory Integration Example for Augment Adam

This script demonstrates how to use different memory types and integrate them.
"""

from augment_adam.core import Assistant
from augment_adam.memory import FAISSMemory, EpisodicMemory, SemanticMemory, WorkingMemory

def main():
    """Run the memory integration example."""
    print("Augment Adam Memory Integration Example")
    print("=" * 50)
    
    # Create different memory systems
    print("\n1. Creating memory systems...")
    
    # Vector-based memory for semantic similarity search
    faiss_memory = FAISSMemory(dimension=384)
    print("   ✓ FAISS Memory created")
    
    # Episodic memory for time-based information
    episodic_memory = EpisodicMemory()
    print("   ✓ Episodic Memory created")
    
    # Semantic memory for concept understanding
    semantic_memory = SemanticMemory()
    print("   ✓ Semantic Memory created")
    
    # Working memory for short-term information
    working_memory = WorkingMemory(capacity=5)
    print("   ✓ Working Memory created")
    
    # Create an assistant with multiple memory systems
    print("\n2. Creating an assistant with integrated memory...")
    assistant = Assistant(
        memory=faiss_memory,
        episodic_memory=episodic_memory,
        semantic_memory=semantic_memory,
        working_memory=working_memory
    )
    print("   ✓ Assistant with integrated memory created")
    
    # Add information to different memory systems
    print("\n3. Adding information to different memory systems...")
    
    # Add to FAISS memory
    faiss_memory.add("The capital of France is Paris.", {"type": "fact", "category": "geography"})
    faiss_memory.add("Python is a programming language.", {"type": "fact", "category": "technology"})
    
    # Add to episodic memory
    episodic_memory.add_episode("User asked about weather in New York", {"timestamp": "2025-04-24T10:30:00"})
    episodic_memory.add_episode("User mentioned they have a meeting tomorrow", {"timestamp": "2025-04-24T10:35:00"})
    
    # Add to semantic memory
    semantic_memory.add_concept("programming", ["coding", "development", "software engineering"])
    semantic_memory.add_concept("weather", ["temperature", "precipitation", "forecast"])
    
    # Add to working memory
    working_memory.add("User's current task: Planning a trip to Paris")
    working_memory.add("User mentioned they need hotel recommendations")
    
    print("   ✓ Information added to all memory systems")
    
    # Demonstrate memory retrieval
    print("\n4. Retrieving information from memory systems...")
    
    # Retrieve from FAISS memory
    query = "What is the capital of France?"
    results = faiss_memory.retrieve(query, n_results=1)
    print(f"   FAISS Query: '{query}'")
    print(f"   Result: '{results[0][0]['text']}' (Score: {results[0][1]:.4f})")
    
    # Retrieve from episodic memory
    recent_episodes = episodic_memory.get_recent_episodes(1)
    print(f"   Recent episode: '{recent_episodes[0]['text']}'")
    
    # Retrieve from semantic memory
    related_concepts = semantic_memory.get_related_concepts("programming")
    print(f"   Concepts related to 'programming': {', '.join(related_concepts)}")
    
    # Retrieve from working memory
    current_context = working_memory.get_all()
    print(f"   Current working memory items: {len(current_context)}")
    for i, item in enumerate(current_context):
        print(f"     {i+1}. {item['text']}")
    
    # Demonstrate assistant with integrated memory
    print("\n5. Chatting with the assistant using integrated memory...")
    questions = [
        "What do you know about Paris?",
        "What was I asking about earlier?",
        "Can you help me with programming?",
        "What am I currently planning?"
    ]
    
    for question in questions:
        print(f"\n   User: {question}")
        response = assistant.chat(question)
        print(f"   Assistant: {response}")
    
    print("\n" + "=" * 50)
    print("Memory Integration Example Completed!")
    print("This example demonstrates how different memory systems can be integrated.")

if __name__ == "__main__":
    main()
