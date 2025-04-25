#!/usr/bin/env python
"""
Quick Start Example for Augment Adam

This script demonstrates the basic usage of Augment Adam.
"""

from augment_adam.core import Assistant
from augment_adam.memory import FAISSMemory

def main():
    """Run the quick start example."""
    print("Augment Adam Quick Start Example")
    print("=" * 40)
    
    # Create a memory system
    print("\n1. Creating a memory system...")
    memory = FAISSMemory()
    print("   ✓ Memory system created")
    
    # Create an assistant
    print("\n2. Creating an assistant...")
    assistant = Assistant(memory=memory)
    print("   ✓ Assistant created")
    
    # Add some memories
    print("\n3. Adding memories...")
    memory.add("My name is Adam.", {"type": "personal"})
    memory.add("I like to help people with AI tasks.", {"type": "preference"})
    memory.add("I was created to assist with complex tasks.", {"type": "background"})
    print("   ✓ Memories added")
    
    # Retrieve memories
    print("\n4. Retrieving memories...")
    query = "What is my name?"
    results = memory.retrieve(query, n_results=1)
    print(f"   Query: '{query}'")
    print(f"   Result: '{results[0][0]['text']}' (Score: {results[0][1]:.4f})")
    
    # Chat with the assistant
    print("\n5. Chatting with the assistant...")
    questions = [
        "Hello, who are you?",
        "What do you like to do?",
        "Can you help me with a coding task?"
    ]
    
    for question in questions:
        print(f"\n   User: {question}")
        response = assistant.chat(question)
        print(f"   Assistant: {response}")
    
    print("\n" + "=" * 40)
    print("Quick Start Example Completed!")
    print("Check out the documentation for more advanced features.")

if __name__ == "__main__":
    main()
