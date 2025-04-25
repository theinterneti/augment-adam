"""
Base classes for semantic memory system.

This module provides the base classes for the semantic memory system,
including the SemanticMemory class, Concept class, and Relation class.
"""

import uuid
import datetime
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Set, Union, Callable, TypeVar
from dataclasses import dataclass, field

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.core.base import Memory, MemoryItem, MemoryType


class RelationType(Enum):
    """
    Types of relations in a semantic memory.
    
    This enum defines the types of relations between concepts in a semantic memory.
    """
    
    IS_A = auto()
    HAS_A = auto()
    PART_OF = auto()
    RELATED_TO = auto()
    SYNONYM_OF = auto()
    ANTONYM_OF = auto()
    INSTANCE_OF = auto()
    SUBCLASS_OF = auto()
    SUPERCLASS_OF = auto()
    ATTRIBUTE_OF = auto()
    CAUSES = auto()
    PRECEDES = auto()
    FOLLOWS = auto()
    SIMILAR_TO = auto()
    OPPOSITE_OF = auto()
    LOCATED_IN = auto()
    USED_FOR = auto()
    MADE_OF = auto()
    DEFINED_AS = auto()
    EXAMPLE_OF = auto()
    CUSTOM = auto()


@dataclass
class Relation:
    """
    Relation between concepts in a semantic memory.
    
    This class represents a relation between concepts in a semantic memory,
    including its type, source, target, and other attributes.
    
    Attributes:
        id: Unique identifier for the relation.
        source_id: ID of the source concept.
        target_id: ID of the target concept.
        relation_type: Type of relation between the concepts.
        metadata: Additional metadata for the relation.
        created_at: When the relation was created.
        updated_at: When the relation was last updated.
        weight: Weight of the relation (0-1).
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""
    relation_type: Union[RelationType, str] = RelationType.RELATED_TO
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    weight: float = 1.0
    
    def __post_init__(self) -> None:
        """Initialize the relation with timestamps."""
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
        
        # Convert string relation type to enum if needed
        if isinstance(self.relation_type, str):
            try:
                self.relation_type = RelationType[self.relation_type]
            except KeyError:
                self.relation_type = RelationType.CUSTOM
                self.metadata["custom_relation_type"] = self.relation_type
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the relation to a dictionary.
        
        Returns:
            Dictionary representation of the relation.
        """
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.name if isinstance(self.relation_type, RelationType) else self.relation_type,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "weight": self.weight,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relation':
        """
        Create a relation from a dictionary.
        
        Args:
            data: Dictionary representation of the relation.
            
        Returns:
            Relation.
        """
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            source_id=data.get("source_id", ""),
            target_id=data.get("target_id", ""),
            relation_type=data.get("relation_type", RelationType.RELATED_TO),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            weight=data.get("weight", 1.0),
        )


@dataclass
class Concept(MemoryItem):
    """
    Concept in a semantic memory.
    
    This class represents a concept in a semantic memory, including its name,
    description, attributes, and other properties.
    
    Attributes:
        id: Unique identifier for the concept.
        content: The content of the concept.
        metadata: Additional metadata for the concept.
        created_at: When the concept was created.
        updated_at: When the concept was last updated.
        expires_at: When the concept expires (if applicable).
        importance: Importance score for the concept (0-1).
        embedding: Vector embedding for the concept (if applicable).
        name: The name of the concept.
        description: Description of the concept.
        attributes: Dictionary of attributes for the concept.
        examples: List of examples of the concept.
        relations: Dictionary of relations to other concepts, keyed by relation ID.
    
    TODO(Issue #6): Add support for concept versioning
    TODO(Issue #6): Implement concept validation
    """
    
    name: str = ""
    description: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    relations: Dict[str, Relation] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize the concept with timestamps."""
        super().__post_init__()
        
        # If content is not provided but name is, use name as content
        if self.content is None and self.name:
            self.content = self.name
    
    def add_relation(self, relation: Relation) -> str:
        """
        Add a relation to another concept.
        
        Args:
            relation: The relation to add.
            
        Returns:
            The ID of the added relation.
        """
        self.relations[relation.id] = relation
        self.updated_at = datetime.datetime.now().isoformat()
        return relation.id
    
    def get_relation(self, relation_id: str) -> Optional[Relation]:
        """
        Get a relation by ID.
        
        Args:
            relation_id: The ID of the relation to get.
            
        Returns:
            The relation, or None if it doesn't exist.
        """
        return self.relations.get(relation_id)
    
    def remove_relation(self, relation_id: str) -> bool:
        """
        Remove a relation.
        
        Args:
            relation_id: The ID of the relation to remove.
            
        Returns:
            True if the relation was removed, False otherwise.
        """
        if relation_id in self.relations:
            del self.relations[relation_id]
            self.updated_at = datetime.datetime.now().isoformat()
            return True
        
        return False
    
    def get_relations_by_type(self, relation_type: Union[RelationType, str]) -> List[Relation]:
        """
        Get relations by type.
        
        Args:
            relation_type: The type of relations to get.
            
        Returns:
            List of relations of the specified type.
        """
        # Convert string relation type to enum if needed
        if isinstance(relation_type, str):
            try:
                relation_type = RelationType[relation_type]
            except KeyError:
                relation_type = RelationType.CUSTOM
        
        return [relation for relation in self.relations.values() if relation.relation_type == relation_type]
    
    def get_relations_to_concept(self, concept_id: str) -> List[Relation]:
        """
        Get relations to a specific concept.
        
        Args:
            concept_id: The ID of the concept.
            
        Returns:
            List of relations to the specified concept.
        """
        return [relation for relation in self.relations.values() if relation.target_id == concept_id]
    
    def add_attribute(self, key: str, value: Any) -> None:
        """
        Add an attribute to the concept.
        
        Args:
            key: The key for the attribute.
            value: The value for the attribute.
        """
        self.attributes[key] = value
        self.updated_at = datetime.datetime.now().isoformat()
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Get an attribute of the concept.
        
        Args:
            key: The key for the attribute.
            default: The default value to return if the attribute doesn't exist.
            
        Returns:
            The attribute value, or the default value if the attribute doesn't exist.
        """
        return self.attributes.get(key, default)
    
    def remove_attribute(self, key: str) -> bool:
        """
        Remove an attribute from the concept.
        
        Args:
            key: The key for the attribute to remove.
            
        Returns:
            True if the attribute was removed, False otherwise.
        """
        if key in self.attributes:
            del self.attributes[key]
            self.updated_at = datetime.datetime.now().isoformat()
            return True
        
        return False
    
    def add_example(self, example: str) -> None:
        """
        Add an example to the concept.
        
        Args:
            example: The example to add.
        """
        if example not in self.examples:
            self.examples.append(example)
            self.updated_at = datetime.datetime.now().isoformat()
    
    def remove_example(self, example: str) -> bool:
        """
        Remove an example from the concept.
        
        Args:
            example: The example to remove.
            
        Returns:
            True if the example was removed, False otherwise.
        """
        if example in self.examples:
            self.examples.remove(example)
            self.updated_at = datetime.datetime.now().isoformat()
            return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the concept to a dictionary.
        
        Returns:
            Dictionary representation of the concept.
        """
        data = super().to_dict()
        data["name"] = self.name
        data["description"] = self.description
        data["attributes"] = self.attributes
        data["examples"] = self.examples
        data["relations"] = {relation_id: relation.to_dict() for relation_id, relation in self.relations.items()}
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Concept':
        """
        Create a concept from a dictionary.
        
        Args:
            data: Dictionary representation of the concept.
            
        Returns:
            Concept.
        """
        concept = super().from_dict(data)
        concept.name = data.get("name", "")
        concept.description = data.get("description", "")
        concept.attributes = data.get("attributes", {})
        concept.examples = data.get("examples", [])
        
        # Add relations
        for relation_data in data.get("relations", {}).values():
            relation = Relation.from_dict(relation_data)
            concept.relations[relation.id] = relation
        
        return concept


T = TypeVar('T', bound=Concept)


@tag("memory.semantic")
class SemanticMemory(Memory[T]):
    """
    Semantic memory system.
    
    This class implements a semantic memory system for storing and retrieving
    conceptual knowledge.
    
    Attributes:
        name: The name of the memory system.
        items: Dictionary of concepts in memory, keyed by ID.
        metadata: Additional metadata for the memory system.
    
    TODO(Issue #6): Add support for memory persistence
    TODO(Issue #6): Implement memory validation
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the semantic memory system.
        
        Args:
            name: The name of the memory system.
        """
        super().__init__(name, MemoryType.SEMANTIC)
    
    def add_relation(self, source_id: str, target_id: str, relation_type: Union[RelationType, str], metadata: Optional[Dict[str, Any]] = None, weight: float = 1.0) -> Optional[str]:
        """
        Add a relation between two concepts.
        
        Args:
            source_id: The ID of the source concept.
            target_id: The ID of the target concept.
            relation_type: The type of relation.
            metadata: Additional metadata for the relation.
            weight: Weight of the relation (0-1).
            
        Returns:
            The ID of the added relation, or None if either concept doesn't exist.
        """
        # Check if both concepts exist
        source = self.get(source_id)
        target = self.get(target_id)
        
        if source is None or target is None:
            return None
        
        # Create the relation
        relation = Relation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            metadata=metadata or {},
            weight=weight
        )
        
        # Add the relation to the source concept
        return source.add_relation(relation)
    
    def get_relation(self, concept_id: str, relation_id: str) -> Optional[Relation]:
        """
        Get a relation from a concept.
        
        Args:
            concept_id: The ID of the concept.
            relation_id: The ID of the relation.
            
        Returns:
            The relation, or None if the concept or relation doesn't exist.
        """
        concept = self.get(concept_id)
        if concept is None:
            return None
        
        return concept.get_relation(relation_id)
    
    def remove_relation(self, concept_id: str, relation_id: str) -> bool:
        """
        Remove a relation from a concept.
        
        Args:
            concept_id: The ID of the concept.
            relation_id: The ID of the relation.
            
        Returns:
            True if the relation was removed, False otherwise.
        """
        concept = self.get(concept_id)
        if concept is None:
            return False
        
        return concept.remove_relation(relation_id)
    
    def get_relations_by_type(self, concept_id: str, relation_type: Union[RelationType, str]) -> List[Relation]:
        """
        Get relations from a concept by type.
        
        Args:
            concept_id: The ID of the concept.
            relation_type: The type of relations to get.
            
        Returns:
            List of relations of the specified type, or an empty list if the concept doesn't exist.
        """
        concept = self.get(concept_id)
        if concept is None:
            return []
        
        return concept.get_relations_by_type(relation_type)
    
    def get_relations_between(self, concept1_id: str, concept2_id: str) -> List[Relation]:
        """
        Get relations between two concepts.
        
        Args:
            concept1_id: The ID of the first concept.
            concept2_id: The ID of the second concept.
            
        Returns:
            List of relations between the concepts, or an empty list if either concept doesn't exist.
        """
        concept1 = self.get(concept1_id)
        concept2 = self.get(concept2_id)
        
        if concept1 is None or concept2 is None:
            return []
        
        # Get relations from concept1 to concept2
        relations1to2 = concept1.get_relations_to_concept(concept2_id)
        
        # Get relations from concept2 to concept1
        relations2to1 = concept2.get_relations_to_concept(concept1_id)
        
        return relations1to2 + relations2to1
    
    def add_attribute(self, concept_id: str, key: str, value: Any) -> bool:
        """
        Add an attribute to a concept.
        
        Args:
            concept_id: The ID of the concept.
            key: The key for the attribute.
            value: The value for the attribute.
            
        Returns:
            True if the attribute was added, False if the concept doesn't exist.
        """
        concept = self.get(concept_id)
        if concept is None:
            return False
        
        concept.add_attribute(key, value)
        return True
    
    def get_attribute(self, concept_id: str, key: str, default: Any = None) -> Any:
        """
        Get an attribute from a concept.
        
        Args:
            concept_id: The ID of the concept.
            key: The key for the attribute.
            default: The default value to return if the attribute doesn't exist.
            
        Returns:
            The attribute value, or the default value if the concept or attribute doesn't exist.
        """
        concept = self.get(concept_id)
        if concept is None:
            return default
        
        return concept.get_attribute(key, default)
    
    def remove_attribute(self, concept_id: str, key: str) -> bool:
        """
        Remove an attribute from a concept.
        
        Args:
            concept_id: The ID of the concept.
            key: The key for the attribute to remove.
            
        Returns:
            True if the attribute was removed, False otherwise.
        """
        concept = self.get(concept_id)
        if concept is None:
            return False
        
        return concept.remove_attribute(key)
    
    def add_example(self, concept_id: str, example: str) -> bool:
        """
        Add an example to a concept.
        
        Args:
            concept_id: The ID of the concept.
            example: The example to add.
            
        Returns:
            True if the example was added, False if the concept doesn't exist.
        """
        concept = self.get(concept_id)
        if concept is None:
            return False
        
        concept.add_example(example)
        return True
    
    def remove_example(self, concept_id: str, example: str) -> bool:
        """
        Remove an example from a concept.
        
        Args:
            concept_id: The ID of the concept.
            example: The example to remove.
            
        Returns:
            True if the example was removed, False otherwise.
        """
        concept = self.get(concept_id)
        if concept is None:
            return False
        
        return concept.remove_example(example)
    
    def search(self, query: Any, limit: int = 10) -> List[T]:
        """
        Search for concepts in memory.
        
        Args:
            query: The query to search for.
            limit: The maximum number of results to return.
            
        Returns:
            List of concepts that match the query.
        """
        # If the query is a string, search for concepts with matching name or description
        if isinstance(query, str):
            results = []
            
            for concept in self.items.values():
                # Check if the concept name contains the query
                if query.lower() in concept.name.lower():
                    results.append(concept)
                    continue
                
                # Check if the concept description contains the query
                if query.lower() in concept.description.lower():
                    results.append(concept)
                    continue
                
                # Check if any example contains the query
                for example in concept.examples:
                    if query.lower() in example.lower():
                        results.append(concept)
                        break
            
            return results[:limit]
        
        # If the query is a dictionary, search for concepts with matching attributes
        elif isinstance(query, dict):
            results = []
            
            for concept in self.items.values():
                # Check if all query attributes match
                match = True
                for key, value in query.items():
                    if key not in concept.attributes or concept.attributes[key] != value:
                        match = False
                        break
                
                if match:
                    results.append(concept)
            
            return results[:limit]
        
        # Otherwise, use the default search
        return super().search(query, limit)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the semantic memory system to a dictionary.
        
        Returns:
            Dictionary representation of the semantic memory system.
        """
        return super().to_dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticMemory':
        """
        Create a semantic memory system from a dictionary.
        
        Args:
            data: Dictionary representation of the semantic memory system.
            
        Returns:
            Semantic memory system.
        """
        memory = cls(name=data.get("name", ""))
        memory.metadata = data.get("metadata", {})
        
        for item_data in data.get("items", {}).values():
            item = Concept.from_dict(item_data)
            memory.add(item)
        
        return memory
