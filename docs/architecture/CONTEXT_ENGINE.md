# Context Engine

## Overview

This document describes the architecture of the Context Engine in Augment Adam. The Context Engine is responsible for managing and retrieving relevant context for the assistant, enabling it to provide more accurate and contextually appropriate responses.

## Architecture Diagram

The Context Engine architecture consists of several components that work together to provide a flexible and powerful context management system.

```
                  +----------------+
                  |  ContextEngine  |
                  +-------+--------+
                          |
          +---------------+---------------+
          |               |               |
+---------v------+ +------v-------+ +-----v--------+
|    Chunking    | |   Retrieval   | |  Composition  |
|    Component   | |   Component   | |   Component   |
+-------+-------+ +------+-------+ +-----+--------+
        |                |               |
+-------v-------+ +------v-------+ +-----v--------+
| TextChunker    | | VectorRetriever| | ContextComposer|
| RecursiveChunker| | HybridRetriever| | PromptComposer |
| SemanticChunker| | GraphRetriever | | ChainComposer  |
+---------------+ +--------------+ +--------------+
```

## Components

### Context Engine

The Context Engine is the main entry point for context management. It coordinates the chunking, retrieval, and composition components to provide relevant context for the assistant.

#### Responsibilities

- Manage the overall context retrieval process
- Coordinate chunking, retrieval, and composition components
- Provide a simple interface for retrieving context
- Cache frequently used contexts for performance

#### Interfaces

- `add_document(document: str, metadata: Optional[Dict[str, Any]] = None) -> str`: Add a document to the context engine.
- `get_context(query: str, k: int = 5) -> str`: Get relevant context for a query.
- `clear() -> None`: Clear all documents from the context engine.

#### Implementation

The Context Engine is implemented as a class that coordinates the chunking, retrieval, and composition components:

```python
from typing import Dict, List, Any, Optional

from augment_adam.context_engine.chunking import Chunker, TextChunker
from augment_adam.context_engine.retrieval import Retriever, VectorRetriever
from augment_adam.context_engine.composition import ContextComposer
from augment_adam.memory import Memory, FAISSMemory

class ContextEngine:
    """Context Engine for managing and retrieving relevant context."""
    
    def __init__(self, 
                 chunker: Optional[Chunker] = None,
                 retriever: Optional[Retriever] = None,
                 composer: Optional[ContextComposer] = None,
                 memory: Optional[Memory] = None):
        """Initialize the context engine.
        
        Args:
            chunker: Chunker for splitting documents into chunks.
            retriever: Retriever for retrieving relevant chunks.
            composer: Composer for composing chunks into context.
            memory: Memory for storing chunks.
        """
        self.chunker = chunker or TextChunker()
        self.memory = memory or FAISSMemory(path="./data/context_engine")
        self.retriever = retriever or VectorRetriever(memory=self.memory)
        self.composer = composer or ContextComposer()
        self.document_ids = {}
        
    def add_document(self, document: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a document to the context engine.
        
        Args:
            document: Document to add.
            metadata: Optional metadata for the document.
            
        Returns:
            ID of the document.
        """
        # Generate a unique ID for the document
        import uuid
        document_id = str(uuid.uuid4())
        
        # Store the document ID
        self.document_ids[document_id] = True
        
        # Add metadata about the document
        doc_metadata = metadata or {}
        doc_metadata["document_id"] = document_id
        
        # Chunk the document
        chunks = self.chunker.chunk(document)
        
        # Store the chunks in memory
        chunk_ids = []
        for i, chunk in enumerate(chunks):
            # Add chunk metadata
            chunk_metadata = doc_metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["chunk_count"] = len(chunks)
            
            # Store the chunk
            chunk_id = self.memory.add(chunk, chunk_metadata)
            chunk_ids.append(chunk_id)
        
        return document_id
    
    def get_context(self, query: str, k: int = 5) -> str:
        """Get relevant context for a query.
        
        Args:
            query: Query to get context for.
            k: Number of chunks to retrieve.
            
        Returns:
            Relevant context for the query.
        """
        # Retrieve relevant chunks
        chunks = self.retriever.retrieve(query, k=k)
        
        # Compose chunks into context
        context = self.composer.compose(query, chunks)
        
        return context
    
    def clear(self) -> None:
        """Clear all documents from the context engine."""
        self.memory.clear()
        self.document_ids = {}
```

### Chunking Component

The Chunking Component is responsible for splitting documents into smaller, manageable chunks that can be stored and retrieved efficiently.

#### Responsibilities

- Split documents into chunks
- Ensure chunks are semantically meaningful
- Handle different types of documents
- Optimize chunk size for retrieval

#### Interfaces

- `chunk(text: str) -> List[str]`: Split a text into chunks.

#### Implementation

The Chunking Component is implemented as an abstract base class with several concrete implementations:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Chunker(ABC):
    """Base class for chunkers."""
    
    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        """Split a text into chunks.
        
        Args:
            text: Text to split into chunks.
            
        Returns:
            List of chunks.
        """
        pass

class TextChunker(Chunker):
    """Chunker that splits text by paragraphs and sentences."""
    
    def __init__(self, chunk_size: int = 1024, overlap: int = 128):
        """Initialize the text chunker.
        
        Args:
            chunk_size: Maximum size of chunks in characters.
            overlap: Overlap between chunks in characters.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, text: str) -> List[str]:
        """Split a text into chunks.
        
        Args:
            text: Text to split into chunks.
            
        Returns:
            List of chunks.
        """
        # Split text into paragraphs
        paragraphs = text.split("\n\n")
        
        # Initialize chunks
        chunks = []
        current_chunk = ""
        
        # Process paragraphs
        for paragraph in paragraphs:
            # If adding the paragraph would exceed the chunk size,
            # add the current chunk to the list and start a new one
            if len(current_chunk) + len(paragraph) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If the paragraph itself is larger than the chunk size,
                # split it into sentences
                if len(paragraph) > self.chunk_size:
                    sentences = paragraph.split(". ")
                    current_chunk = ""
                    
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) > self.chunk_size:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = sentence + ". "
                        else:
                            current_chunk += sentence + ". "
                else:
                    current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += paragraph
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
        
        # Add overlap between chunks
        if self.overlap > 0 and len(chunks) > 1:
            overlapped_chunks = [chunks[0]]
            
            for i in range(1, len(chunks)):
                prev_chunk = chunks[i-1]
                current_chunk = chunks[i]
                
                # Add overlap from the end of the previous chunk
                if len(prev_chunk) > self.overlap:
                    overlap_text = prev_chunk[-self.overlap:]
                    overlapped_chunks.append(overlap_text + current_chunk)
                else:
                    overlapped_chunks.append(current_chunk)
            
            chunks = overlapped_chunks
        
        return chunks
```

### Retrieval Component

The Retrieval Component is responsible for retrieving relevant chunks from memory based on a query.

#### Responsibilities

- Retrieve relevant chunks from memory
- Rank chunks by relevance
- Support different retrieval strategies
- Optimize retrieval for performance

#### Interfaces

- `retrieve(query: str, k: int = 5) -> List[Dict[str, Any]]`: Retrieve relevant chunks for a query.

#### Implementation

The Retrieval Component is implemented as an abstract base class with several concrete implementations:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from augment_adam.memory import Memory, FAISSMemory

class Retriever(ABC):
    """Base class for retrievers."""
    
    @abstractmethod
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks for a query.
        
        Args:
            query: Query to retrieve chunks for.
            k: Number of chunks to retrieve.
            
        Returns:
            List of chunks with metadata.
        """
        pass

class VectorRetriever(Retriever):
    """Retriever that uses vector similarity to retrieve chunks."""
    
    def __init__(self, memory: Optional[Memory] = None):
        """Initialize the vector retriever.
        
        Args:
            memory: Memory to retrieve chunks from.
        """
        self.memory = memory or FAISSMemory(path="./data/context_engine")
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks for a query.
        
        Args:
            query: Query to retrieve chunks for.
            k: Number of chunks to retrieve.
            
        Returns:
            List of chunks with metadata.
        """
        # Search for similar chunks in memory
        results = self.memory.search(query, k=k)
        
        # Format the results
        chunks = []
        for result in results:
            chunks.append({
                "text": result["text"],
                "metadata": result["metadata"],
                "score": result["score"]
            })
        
        return chunks
```

### Composition Component

The Composition Component is responsible for composing retrieved chunks into a coherent context that can be used by the assistant.

#### Responsibilities

- Compose chunks into a coherent context
- Format context for the assistant
- Handle different types of contexts
- Optimize context for the assistant

#### Interfaces

- `compose(query: str, chunks: List[Dict[str, Any]]) -> str`: Compose chunks into a context.

#### Implementation

The Composition Component is implemented as a class that composes chunks into a context:

```python
from typing import List, Dict, Any

class ContextComposer:
    """Composer for composing chunks into context."""
    
    def __init__(self, max_context_length: int = 4096):
        """Initialize the context composer.
        
        Args:
            max_context_length: Maximum length of the context in characters.
        """
        self.max_context_length = max_context_length
    
    def compose(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """Compose chunks into a context.
        
        Args:
            query: Query that the context is for.
            chunks: Chunks to compose into a context.
            
        Returns:
            Composed context.
        """
        # Sort chunks by score
        sorted_chunks = sorted(chunks, key=lambda x: x["score"], reverse=True)
        
        # Compose context
        context = f"Query: {query}\n\nRelevant Context:\n\n"
        
        # Add chunks to context
        for i, chunk in enumerate(sorted_chunks):
            # Add chunk header
            chunk_header = f"Chunk {i+1} (Score: {chunk['score']:.2f}):\n"
            
            # Add chunk text
            chunk_text = chunk["text"]
            
            # Add chunk to context
            if len(context) + len(chunk_header) + len(chunk_text) + 2 <= self.max_context_length:
                context += chunk_header + chunk_text + "\n\n"
            else:
                # If adding the chunk would exceed the max context length,
                # truncate the chunk
                remaining_length = self.max_context_length - len(context) - len(chunk_header) - 2
                if remaining_length > 0:
                    context += chunk_header + chunk_text[:remaining_length] + "...\n\n"
                break
        
        return context
```



## Interfaces

### Context Engine Interface

The Context Engine provides a simple interface for managing and retrieving context.

```python
from typing import Dict, Any, Optional

class ContextEngineInterface:
    """Interface for the Context Engine."""
    
    def add_document(self, document: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a document to the context engine.
        
        Args:
            document: Document to add.
            metadata: Optional metadata for the document.
            
        Returns:
            ID of the document.
        """
        pass
    
    def get_context(self, query: str, k: int = 5) -> str:
        """Get relevant context for a query.
        
        Args:
            query: Query to get context for.
            k: Number of chunks to retrieve.
            
        Returns:
            Relevant context for the query.
        """
        pass
    
    def clear(self) -> None:
        """Clear all documents from the context engine."""
        pass
```



## Workflows

### Adding a Document

The process of adding a document to the context engine.

#### Steps

1. Create a context engine instance
2. Prepare the document and metadata
3. Call the add_document method
4. The document is chunked by the chunker
5. Chunks are stored in memory
6. The document ID is returned

#### Diagram

```
User -> ContextEngine: add_document(document, metadata)
ContextEngine -> Chunker: chunk(document)
Chunker -> ContextEngine: chunks
ContextEngine -> Memory: add(chunk, metadata)
Memory -> ContextEngine: chunk_id
ContextEngine -> User: document_id
```

### Retrieving Context

The process of retrieving relevant context for a query.

#### Steps

1. Create a context engine instance
2. Prepare the query
3. Call the get_context method
4. The retriever retrieves relevant chunks
5. The composer composes the chunks into a context
6. The context is returned

#### Diagram

```
User -> ContextEngine: get_context(query, k)
ContextEngine -> Retriever: retrieve(query, k)
Retriever -> Memory: search(query, k)
Memory -> Retriever: chunks
Retriever -> ContextEngine: chunks
ContextEngine -> Composer: compose(query, chunks)
Composer -> ContextEngine: context
ContextEngine -> User: context
```



## Examples

### Basic Usage

Example of basic usage of the context engine.

```python
from augment_adam.context_engine import ContextEngine

# Create a context engine
context_engine = ContextEngine()

# Add documents to the context engine
document_id1 = context_engine.add_document(
    "Python is a high-level, interpreted programming language. "
    "It was created by Guido van Rossum and first released in 1991. "
    "Python's design philosophy emphasizes code readability with its "
    "notable use of significant whitespace."
)

document_id2 = context_engine.add_document(
    "JavaScript is a high-level, interpreted programming language. "
    "It was created by Brendan Eich and first released in 1995. "
    "JavaScript is primarily used for web development and is an "
    "essential part of web applications."
)

# Get context for a query
query = "When was Python created and by whom?"
context = context_engine.get_context(query)
print(context)
```

### Custom Components

Example of using custom components with the context engine.

```python
from augment_adam.context_engine import ContextEngine
from augment_adam.context_engine.chunking import RecursiveChunker
from augment_adam.context_engine.retrieval import HybridRetriever
from augment_adam.context_engine.composition import PromptComposer
from augment_adam.memory import FAISSMemory

# Create custom components
chunker = RecursiveChunker(chunk_size=512, overlap=64)
memory = FAISSMemory(path="./data/custom_context_engine")
retriever = HybridRetriever(memory=memory)
composer = PromptComposer(max_context_length=2048)

# Create a context engine with custom components
context_engine = ContextEngine(
    chunker=chunker,
    retriever=retriever,
    composer=composer,
    memory=memory
)

# Add a document to the context engine
document_id = context_engine.add_document(
    "The Context Engine is a core component of the Augment Adam framework "
    "that provides a way to manage and retrieve relevant context for the assistant. "
    "It consists of three main components: the Chunking Component, the Retrieval Component, "
    "and the Composition Component."
)

# Get context for a query
query = "What are the main components of the Context Engine?"
context = context_engine.get_context(query)
print(context)
```



## Integration with Other Components

### Memory System

The Context Engine integrates with the Memory System to store and retrieve chunks.

```python
from augment_adam.context_engine import ContextEngine
from augment_adam.memory import FAISSMemory

# Create a memory
memory = FAISSMemory(path="./data/context_engine")

# Create a context engine with the memory
context_engine = ContextEngine(memory=memory)

# Add a document to the context engine
document_id = context_engine.add_document(
    "The Memory System is a core component of the Augment Adam framework "
    "that provides a way to store and retrieve information. It includes "
    "vector-based, graph-based, episodic, and semantic memory systems."
)

# Get context for a query
query = "What is the Memory System?"
context = context_engine.get_context(query)
print(context)
```

### Assistant

The Context Engine integrates with the Assistant to provide relevant context for queries.

```python
from augment_adam.core import Assistant
from augment_adam.context_engine import ContextEngine

# Create a context engine
context_engine = ContextEngine()

# Add documents to the context engine
context_engine.add_document(
    "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. "
    "It is named after the engineer Gustave Eiffel, whose company designed and built the tower. "
    "Constructed from 1887 to 1889 as the entrance to the 1889 World's Fair, it was initially "
    "criticized by some of France's leading artists and intellectuals for its design, but it "
    "has become a global cultural icon of France and one of the most recognizable structures "
    "in the world."
)

# Create an assistant with the context engine
assistant = Assistant(context_engine=context_engine)

# Chat with the assistant
response = assistant.chat("When was the Eiffel Tower built?")
print(response)
```



## Future Enhancements

- **Context Versioning**: Add support for versioning context to track changes over time.
- **Context Validation**: Implement validation for context to ensure data integrity.
- **Context Analytics**: Add analytics to track context usage and performance.
- **Advanced Chunking Strategies**: Implement more sophisticated chunking strategies, such as semantic chunking and hierarchical chunking.
- **Multi-Modal Context**: Add support for multi-modal context, including images, audio, and video.
- **Context Caching**: Implement intelligent caching for frequently used contexts.
- **Context Compression**: Implement compression techniques to reduce context storage requirements.
- **Context Encryption**: Add encryption for sensitive context information.
- **Context Synchronization**: Implement synchronization between different context engine instances.

