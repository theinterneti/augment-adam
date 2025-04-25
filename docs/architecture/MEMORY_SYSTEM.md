# Memory System

## Overview

This document describes the architecture of the Memory System in Augment Adam. The Memory System provides various memory implementations for storing and retrieving information, including vector-based, graph-based, episodic, and semantic memory systems.

## Architecture Diagram

The Memory System architecture consists of several components that work together to provide a flexible and powerful memory system.

```
                  +----------------+
                  |    Memory     |
                  |  (Interface)  |
                  +-------+-------+
                          |
          +---------------+---------------+
          |               |               |
+---------v------+ +------v-------+ +-----v--------+
|  VectorMemory  | |  GraphMemory | | OtherMemory  |
|   (Abstract)   | |  (Abstract)  | |  (Abstract)  |
+-------+-------+ +------+-------+ +-----+--------+
        |                |               |
+-------v-------+ +------v-------+ +-----v--------+
|  FAISSMemory  | |   Neo4jMemory | |  CustomMemory |
+---------------+ +--------------+ +--------------+
```

## Components

### Memory Interface

The Memory interface defines the contract that all memory implementations must follow. It provides methods for adding, retrieving, searching, and deleting items from memory.

#### Responsibilities

- Define the contract for memory implementations
- Provide common functionality for all memory implementations
- Enable memory implementations to be used interchangeably

#### Interfaces

- `add(text: str, metadata: Optional[Dict[str, Any]] = None) -> str`: Add a text to memory with optional metadata.
- `search(query: str, k: int = 5) -> List[Dict[str, Any]]`: Search for similar texts in memory.
- `get(id: str) -> Optional[Dict[str, Any]]`: Get a text by ID.
- `delete(id: str) -> bool`: Delete a text by ID.
- `clear() -> None`: Clear all memory.

#### Implementation

The Memory interface is implemented as an abstract base class in Python:

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class Memory(ABC):
    """Base class for all memory implementations."""
    
    def __init__(self):
        """Initialize the memory."""
        self.name = self.__class__.__name__
        self.description = "Base memory implementation"
    
    @abstractmethod
    def add(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a text to memory."""
        pass
    
    @abstractmethod
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar texts in memory."""
        pass
    
    @abstractmethod
    def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a text by ID."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a text by ID."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all memory."""
        pass
```

### Vector Memory

Vector Memory is an abstract base class for vector-based memory implementations. It extends the Memory interface with vector-specific functionality.

#### Responsibilities

- Provide common functionality for vector-based memory implementations
- Handle embedding generation
- Manage vector storage and retrieval

#### Interfaces

- `embed(text: str) -> List[float]`: Generate an embedding for a text.

#### Implementation

The Vector Memory abstract class extends the Memory interface:

```python
from abc import abstractmethod
from typing import Dict, List, Any, Optional

from augment_adam.memory.base import Memory

class VectorMemory(Memory):
    """Base class for vector-based memory implementations."""
    
    def __init__(self, embedding_model: str = "text-embedding-ada-002"):
        """Initialize the vector memory."""
        super().__init__()
        self.description = "Vector-based memory implementation"
        self.embedding_model = embedding_model
        self.embedding_dimension = 1536  # Default for OpenAI embeddings
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate an embedding for a text."""
        pass
```

### FAISS Memory

FAISS Memory is a concrete implementation of Vector Memory that uses Facebook AI Similarity Search (FAISS) for efficient similarity search in high-dimensional spaces.

#### Responsibilities

- Store and retrieve vectors using FAISS
- Generate embeddings for texts
- Persist memory to disk

#### Implementation

The FAISS Memory implementation uses the FAISS library for vector storage and retrieval:

```python
import os
import json
import uuid
import faiss
import numpy as np
from typing import Dict, List, Any, Optional

from augment_adam.memory.vector import VectorMemory
from augment_adam.models import get_embedding

class FAISSMemory(VectorMemory):
    """FAISS-based vector memory implementation."""
    
    def __init__(self, path: str = "./data/faiss", embedding_model: str = "text-embedding-ada-002"):
        """Initialize the FAISS memory."""
        super().__init__(embedding_model=embedding_model)
        self.path = path
        self.description = "FAISS-based vector memory"
        
        # Create the directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(self.embedding_dimension)
        self.texts = {}
        self.metadata = {}
        
        # Load the index if it exists
        self.load()
    
    def embed(self, text: str) -> List[float]:
        """Generate an embedding for a text."""
        return get_embedding(text, model=self.embedding_model)
    
    def add(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a text to memory."""
        # Generate a unique ID
        id = str(uuid.uuid4())
        
        # Generate embedding
        embedding = self.embed(text)
        
        # Add to FAISS index
        self.index.add(np.array([embedding], dtype=np.float32))
        
        # Store text and metadata
        self.texts[id] = text
        self.metadata[id] = metadata or {}
        
        # Save to disk
        self.save()
        
        return id
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar texts in memory."""
        # Generate embedding for the query
        query_embedding = self.embed(query)
        
        # Search the FAISS index
        distances, indices = self.index.search(np.array([query_embedding], dtype=np.float32), k)
        
        # Get the results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.texts):
                continue
            
            id = list(self.texts.keys())[idx]
            results.append({
                "id": id,
                "text": self.texts[id],
                "metadata": self.metadata[id],
                "score": float(1.0 / (1.0 + distances[0][i]))
            })
        
        return results
    
    def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a text by ID."""
        if id not in self.texts:
            return None
        
        return {
            "id": id,
            "text": self.texts[id],
            "metadata": self.metadata[id]
        }
    
    def delete(self, id: str) -> bool:
        """Delete a text by ID."""
        if id not in self.texts:
            return False
        
        # Remove from storage
        del self.texts[id]
        del self.metadata[id]
        
        # Rebuild the index
        self.index = faiss.IndexFlatL2(self.embedding_dimension)
        for text_id, text in self.texts.items():
            embedding = self.embed(text)
            self.index.add(np.array([embedding], dtype=np.float32))
        
        # Save to disk
        self.save()
        
        return True
    
    def clear(self) -> None:
        """Clear all memory."""
        self.index = faiss.IndexFlatL2(self.embedding_dimension)
        self.texts = {}
        self.metadata = {}
        
        # Save to disk
        self.save()
    
    def save(self) -> None:
        """Save the memory to disk."""
        # Save the index
        faiss.write_index(self.index, os.path.join(self.path, "index.faiss"))
        
        # Save the texts and metadata
        with open(os.path.join(self.path, "texts.json"), "w") as f:
            json.dump(self.texts, f)
        
        with open(os.path.join(self.path, "metadata.json"), "w") as f:
            json.dump(self.metadata, f)
    
    def load(self) -> None:
        """Load the memory from disk."""
        # Check if the files exist
        index_path = os.path.join(self.path, "index.faiss")
        texts_path = os.path.join(self.path, "texts.json")
        metadata_path = os.path.join(self.path, "metadata.json")
        
        if not (os.path.exists(index_path) and os.path.exists(texts_path) and os.path.exists(metadata_path)):
            return
        
        # Load the index
        self.index = faiss.read_index(index_path)
        
        # Load the texts and metadata
        with open(texts_path, "r") as f:
            self.texts = json.load(f)
        
        with open(metadata_path, "r") as f:
            self.metadata = json.load(f)
```



## Interfaces

### Memory Registry

The Memory Registry provides a way to register and retrieve memory implementations by name.

```python
from typing import Dict, Type, Any

from augment_adam.memory.base import Memory

# Registry of memory implementations
_memory_registry: Dict[str, Type[Memory]] = {}

def register_memory(name: str, memory_class: Type[Memory]) -> None:
    """Register a memory implementation."""
    _memory_registry[name] = memory_class

def get_memory(name: str, **kwargs: Any) -> Memory:
    """Get a memory implementation by name."""
    if name not in _memory_registry:
        raise ValueError(f"Memory implementation '{name}' not found.")
    
    return _memory_registry[name](**kwargs)
```



## Workflows

### Adding and Retrieving Memory

The process of adding and retrieving items from memory.

#### Steps

1. Create a memory implementation
2. Add a text to memory
3. Get the text by ID
4. Search for similar texts

#### Diagram

```
User -> Memory: add(text, metadata)
Memory -> User: id
User -> Memory: get(id)
Memory -> User: {id, text, metadata}
User -> Memory: search(query, k)
Memory -> User: [{id, text, metadata, score}, ...]
```



## Examples

### Using FAISS Memory

Example of using FAISS memory.

```python
from augment_adam.memory import FAISSMemory

# Create a FAISS memory
memory = FAISSMemory(path="./data/faiss")

# Add texts to memory
id1 = memory.add("Hello, world!", {"source": "example"})
id2 = memory.add("How are you?", {"source": "example"})
id3 = memory.add("Hello, how are you today?", {"source": "example"})

# Search for similar texts
results = memory.search("Hello", k=2)
for result in results:
    print(f"Text: {result['text']}")
    print(f"Score: {result['score']}")
    print(f"Metadata: {result['metadata']}")
    print()
```



## Integration with Other Components

### Context Engine

The Memory System integrates with the Context Engine to provide relevant context for the assistant.

```python
from augment_adam.memory import FAISSMemory
from augment_adam.context_engine import ContextEngine

# Create a memory
memory = FAISSMemory(path="./data/faiss")

# Create a context engine with memory
context_engine = ContextEngine(memory=memory)

# Add documents to the context engine
context_engine.add_document("France is a country in Western Europe. Its capital is Paris.")

# Retrieve context for a query
context = context_engine.get_context("What is the capital of France?")
print(context)
```

### Assistant

The Memory System integrates with the Assistant to provide memory capabilities.

```python
from augment_adam.core import Assistant
from augment_adam.memory import FAISSMemory

# Create a memory
memory = FAISSMemory(path="./data/faiss")

# Create an assistant with memory
assistant = Assistant(memory=memory)

# Chat with the assistant
response = assistant.chat("Remember that my name is Alice.")
print(response)

response = assistant.chat("What's my name?")
print(response)
```



## Future Enhancements

- **Memory Versioning**: Add support for versioning memory items to track changes over time.
- **Memory Validation**: Implement validation for memory items to ensure data integrity.
- **Memory Analytics**: Add analytics to track memory usage and performance.
- **Memory Persistence**: Enhance persistence options with support for more storage backends.
- **Memory Compression**: Implement compression techniques to reduce memory storage requirements.
- **Memory Encryption**: Add encryption for sensitive memory items.
- **Memory Synchronization**: Implement synchronization between different memory instances.

