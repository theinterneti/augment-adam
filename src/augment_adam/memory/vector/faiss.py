"""
FAISS-based vector memory system.

This module provides a vector memory system based on FAISS (Facebook AI Similarity Search),
which is a library for efficient similarity search and clustering of dense vectors.
"""

import os
import json
import numpy as np
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar, cast
import faiss

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.vector.base import VectorMemory, VectorMemoryItem


@tag("memory.vector.faiss")
class FAISSMemory(VectorMemory[VectorMemoryItem]):
    """
    FAISS-based vector memory system.
    
    This class implements a vector memory system using FAISS for efficient
    similarity search of dense vectors.
    
    Attributes:
        name: The name of the memory system.
        dimension: The dimension of the vector embeddings.
        index: The FAISS index for similarity search.
        items: Dictionary of items in memory, keyed by ID.
        metadata: Additional metadata for the memory system.
        id_to_index: Mapping from item IDs to FAISS index positions.
        index_to_id: Mapping from FAISS index positions to item IDs.
    
    TODO(Issue #6): Add support for memory persistence
    TODO(Issue #6): Implement memory validation
    """
    
    def __init__(self, name: str, dimension: int = 1536, index_type: str = "Flat") -> None:
        """
        Initialize the FAISS memory system.
        
        Args:
            name: The name of the memory system.
            dimension: The dimension of the vector embeddings.
            index_type: The type of FAISS index to use.
        """
        super().__init__(name, dimension)
        
        # Create FAISS index
        if index_type == "Flat":
            self.index = faiss.IndexFlatL2(dimension)
        elif index_type == "IVF":
            # IVF index requires training, so we use a flat index for now
            # and will train it when we have enough data
            quantizer = faiss.IndexFlatL2(dimension)
            self.index = faiss.IndexIVFFlat(quantizer, dimension, 100)
            self.index.nprobe = 10
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        self.id_to_index: Dict[str, int] = {}
        self.index_to_id: Dict[int, str] = {}
        
        self.metadata["index_type"] = index_type
    
    def add(self, item: VectorMemoryItem) -> str:
        """
        Add an item to memory.
        
        Args:
            item: The item to add to memory.
            
        Returns:
            The ID of the added item.
        """
        # If the item doesn't have an embedding, generate one
        if item.embedding is None and item.text is not None:
            item.embedding = self.generate_embedding(item.text)
        
        # Add the item to the dictionary
        super().add(item)
        
        # Add the embedding to the FAISS index
        if item.embedding is not None:
            embedding_np = np.array([item.embedding], dtype=np.float32)
            
            # If the index is IVF and not trained, train it
            if isinstance(self.index, faiss.IndexIVFFlat) and not self.index.is_trained:
                if len(self.items) >= 100:
                    # Collect all embeddings
                    embeddings = np.array([i.embedding for i in self.items.values() if i.embedding is not None], dtype=np.float32)
                    # Train the index
                    self.index.train(embeddings)
            
            # Add the embedding to the index
            index = self.index.ntotal
            self.index.add(embedding_np)
            
            # Update the mappings
            self.id_to_index[item.id] = index
            self.index_to_id[index] = item.id
        
        return item.id
    
    def update(self, item_id: str, content: Any = None, metadata: Dict[str, Any] = None) -> Optional[VectorMemoryItem]:
        """
        Update an item in memory.
        
        Args:
            item_id: The ID of the item to update.
            content: New content for the item.
            metadata: New metadata for the item.
            
        Returns:
            The updated item, or None if it doesn't exist.
        """
        # Get the original item
        original_item = self.get(item_id)
        if original_item is None:
            return None
        
        # Update the item
        updated_item = super().update(item_id, content, metadata)
        
        # If the embedding changed, update the FAISS index
        if (updated_item is not None and updated_item.embedding is not None and
                (original_item.embedding is None or original_item.embedding != updated_item.embedding)):
            # FAISS doesn't support updating, so we need to remove and re-add
            if item_id in self.id_to_index:
                # Remove the old embedding
                index = self.id_to_index[item_id]
                # Note: FAISS doesn't support removing individual vectors
                # In a real implementation, you would need to rebuild the index
                
                # Add the new embedding
                embedding_np = np.array([updated_item.embedding], dtype=np.float32)
                new_index = self.index.ntotal
                self.index.add(embedding_np)
                
                # Update the mappings
                self.id_to_index[item_id] = new_index
                self.index_to_id[new_index] = item_id
                del self.index_to_id[index]
            else:
                # Add the new embedding
                embedding_np = np.array([updated_item.embedding], dtype=np.float32)
                index = self.index.ntotal
                self.index.add(embedding_np)
                
                # Update the mappings
                self.id_to_index[item_id] = index
                self.index_to_id[index] = item_id
        
        return updated_item
    
    def remove(self, item_id: str) -> bool:
        """
        Remove an item from memory.
        
        Args:
            item_id: The ID of the item to remove.
            
        Returns:
            True if the item was removed, False otherwise.
        """
        # Remove the item from the dictionary
        if not super().remove(item_id):
            return False
        
        # Remove the item from the FAISS index
        if item_id in self.id_to_index:
            index = self.id_to_index[item_id]
            # Note: FAISS doesn't support removing individual vectors
            # In a real implementation, you would need to rebuild the index
            
            # Update the mappings
            del self.id_to_index[item_id]
            del self.index_to_id[index]
        
        return True
    
    def clear(self) -> None:
        """Remove all items from memory."""
        super().clear()
        
        # Reset the FAISS index
        dimension = self.dimension
        index_type = self.metadata.get("index_type", "Flat")
        
        if index_type == "Flat":
            self.index = faiss.IndexFlatL2(dimension)
        elif index_type == "IVF":
            quantizer = faiss.IndexFlatL2(dimension)
            self.index = faiss.IndexIVFFlat(quantizer, dimension, 100)
            self.index.nprobe = 10
        
        self.id_to_index = {}
        self.index_to_id = {}
    
    def search(self, query: Union[str, List[float]], limit: int = 10) -> List[VectorMemoryItem]:
        """
        Search for items in memory by similarity.
        
        Args:
            query: The query to search for (either a string or a vector embedding).
            limit: The maximum number of results to return.
            
        Returns:
            List of items that match the query, sorted by similarity.
        """
        # If the query is a string, convert it to a vector embedding
        if isinstance(query, str):
            query_embedding = self.generate_embedding(query)
        else:
            query_embedding = query
        
        # Convert the query to a numpy array
        query_np = np.array([query_embedding], dtype=np.float32)
        
        # If the index is empty, return an empty list
        if self.index.ntotal == 0:
            return []
        
        # Search the FAISS index
        distances, indices = self.index.search(query_np, min(limit, self.index.ntotal))
        
        # Convert the results to memory items
        results = []
        for i, idx in enumerate(indices[0]):
            if idx in self.index_to_id:
                item_id = self.index_to_id[idx]
                item = self.get(item_id)
                if item is not None:
                    results.append(item)
        
        return results
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a vector embedding for a text.
        
        Args:
            text: The text to generate an embedding for.
            
        Returns:
            Vector embedding for the text.
        """
        # This is a placeholder implementation
        # In a real implementation, you would use a model to generate embeddings
        # For example, using OpenAI's text-embedding-ada-002 model
        
        # For now, we'll just use a random embedding
        embedding = np.random.randn(self.dimension).astype(np.float32)
        # Normalize the embedding
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.tolist()
    
    def calculate_similarity(self, embedding1: List[float], embedding2: Optional[List[float]]) -> float:
        """
        Calculate the similarity between two vector embeddings.
        
        Args:
            embedding1: The first vector embedding.
            embedding2: The second vector embedding.
            
        Returns:
            Similarity score between the two embeddings (0-1).
        """
        if embedding2 is None:
            return 0.0
        
        # Convert to numpy arrays
        embedding1_np = np.array(embedding1, dtype=np.float32)
        embedding2_np = np.array(embedding2, dtype=np.float32)
        
        # Normalize the embeddings
        embedding1_np = embedding1_np / np.linalg.norm(embedding1_np)
        embedding2_np = embedding2_np / np.linalg.norm(embedding2_np)
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1_np, embedding2_np)
        
        return float(similarity)
    
    def save(self, directory: str) -> None:
        """
        Save the memory system to disk.
        
        Args:
            directory: The directory to save the memory system to.
        """
        os.makedirs(directory, exist_ok=True)
        
        # Save the FAISS index
        faiss.write_index(self.index, os.path.join(directory, "index.faiss"))
        
        # Save the items
        items_data = {item_id: item.to_dict() for item_id, item in self.items.items()}
        with open(os.path.join(directory, "items.json"), "w") as f:
            json.dump(items_data, f)
        
        # Save the mappings
        mappings_data = {
            "id_to_index": self.id_to_index,
            "index_to_id": {int(k): v for k, v in self.index_to_id.items()},
        }
        with open(os.path.join(directory, "mappings.json"), "w") as f:
            json.dump(mappings_data, f)
        
        # Save the metadata
        with open(os.path.join(directory, "metadata.json"), "w") as f:
            json.dump({
                "name": self.name,
                "dimension": self.dimension,
                "memory_type": self.memory_type.name,
                "metadata": self.metadata,
            }, f)
    
    @classmethod
    def load(cls, directory: str) -> 'FAISSMemory':
        """
        Load a memory system from disk.
        
        Args:
            directory: The directory to load the memory system from.
            
        Returns:
            The loaded memory system.
        """
        # Load the metadata
        with open(os.path.join(directory, "metadata.json"), "r") as f:
            metadata_data = json.load(f)
        
        # Create the memory system
        memory = cls(
            name=metadata_data.get("name", ""),
            dimension=metadata_data.get("dimension", 1536),
            index_type=metadata_data.get("metadata", {}).get("index_type", "Flat"),
        )
        
        # Load the FAISS index
        memory.index = faiss.read_index(os.path.join(directory, "index.faiss"))
        
        # Load the items
        with open(os.path.join(directory, "items.json"), "r") as f:
            items_data = json.load(f)
        
        for item_data in items_data.values():
            item = VectorMemoryItem.from_dict(item_data)
            memory.items[item.id] = item
        
        # Load the mappings
        with open(os.path.join(directory, "mappings.json"), "r") as f:
            mappings_data = json.load(f)
        
        memory.id_to_index = mappings_data.get("id_to_index", {})
        memory.index_to_id = {int(k): v for k, v in mappings_data.get("index_to_id", {}).items()}
        
        return memory
