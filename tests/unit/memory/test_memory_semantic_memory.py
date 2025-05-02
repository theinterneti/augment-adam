"""
Unit tests for the Semantic Memory system.

This module contains tests for the Semantic Memory system, including memory
storage, retrieval, and management of concepts and relations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from augment_adam.memory.core.base import MemoryType
from augment_adam.memory.semantic.base import SemanticMemory, Concept, Relation, RelationType


class TestSemanticMemory:
    """Tests for the Semantic Memory system."""

    @pytest.fixture
    def semantic_memory(self):
        """Create a SemanticMemory for testing."""
        return SemanticMemory(name="test_semantic_memory")

    @pytest.fixture
    def sample_concept(self):
        """Create a sample Concept for testing."""
        return Concept(
            name="Test Concept",
            description="A test concept",
            content="Test content",
            attributes={"attribute1": "value1", "attribute2": "value2"},
            examples=["example1", "example2"]
        )

    @pytest.fixture
    def sample_concepts(self, semantic_memory):
        """Create and add sample concepts to memory for testing."""
        concept1 = Concept(
            name="Dog",
            description="A domesticated carnivorous mammal",
            content="Dogs are domesticated mammals, not natural wild animals.",
            attributes={"type": "mammal", "domesticated": True},
            examples=["Labrador", "Poodle"]
        )

        concept2 = Concept(
            name="Animal",
            description="A living organism that feeds on organic matter",
            content="Animals are multicellular eukaryotic organisms.",
            attributes={"type": "organism", "kingdom": "Animalia"},
            examples=["Dog", "Cat", "Elephant"]
        )

        concept1_id = semantic_memory.add(concept1)
        concept2_id = semantic_memory.add(concept2)

        return {"dog": concept1_id, "animal": concept2_id}

    def test_init(self, semantic_memory):
        """Test initializing a SemanticMemory."""
        assert semantic_memory.name == "test_semantic_memory"
        assert semantic_memory.memory_type == MemoryType.SEMANTIC
        assert semantic_memory.items == {}

    def test_concept_init(self, sample_concept):
        """Test initializing a Concept."""
        assert sample_concept.name == "Test Concept"
        assert sample_concept.description == "A test concept"
        assert sample_concept.content == "Test content"
        assert sample_concept.attributes == {"attribute1": "value1", "attribute2": "value2"}
        assert sample_concept.examples == ["example1", "example2"]
        assert sample_concept.id is not None
        assert sample_concept.created_at is not None
        assert sample_concept.updated_at is not None
        assert sample_concept.relations == {}

    def test_relation_init(self):
        """Test initializing a Relation."""
        relation = Relation(
            source_id="source_id",
            target_id="target_id",
            relation_type=RelationType.IS_A,
            metadata={"key": "value"},
            weight=0.8
        )

        assert relation.source_id == "source_id"
        assert relation.target_id == "target_id"
        assert relation.relation_type == RelationType.IS_A
        assert relation.metadata == {"key": "value"}
        assert relation.weight == 0.8
        assert relation.id is not None
        assert relation.created_at is not None
        assert relation.updated_at is not None

    def test_add_concept(self, semantic_memory, sample_concept):
        """Test adding a concept to semantic memory."""
        # Add the concept
        concept_id = semantic_memory.add(sample_concept)

        # Check that the concept was added
        assert concept_id == sample_concept.id
        assert sample_concept.id in semantic_memory.items
        assert semantic_memory.items[sample_concept.id] == sample_concept

    def test_get_concept(self, semantic_memory, sample_concept):
        """Test getting a concept from semantic memory."""
        # Add the concept
        semantic_memory.add(sample_concept)

        # Get the concept
        retrieved_concept = semantic_memory.get(sample_concept.id)

        # Check that the correct concept was retrieved
        assert retrieved_concept == sample_concept

    def test_get_nonexistent_concept(self, semantic_memory):
        """Test getting a nonexistent concept from semantic memory."""
        # Get a nonexistent concept
        retrieved_concept = semantic_memory.get("nonexistent")

        # Check that None was returned
        assert retrieved_concept is None

    def test_update_concept(self, semantic_memory, sample_concept):
        """Test updating a concept in semantic memory."""
        # Add the concept
        semantic_memory.add(sample_concept)

        # Update the concept
        updated_concept = semantic_memory.update(
            sample_concept.id, content="updated content"
        )

        # Check that the concept was updated
        assert updated_concept == sample_concept
        assert updated_concept.content == "updated content"

    def test_update_nonexistent_concept(self, semantic_memory):
        """Test updating a nonexistent concept in semantic memory."""
        # Update a nonexistent concept
        updated_concept = semantic_memory.update(
            "nonexistent", content="updated content"
        )

        # Check that None was returned
        assert updated_concept is None

    def test_remove_concept(self, semantic_memory, sample_concept):
        """Test removing a concept from semantic memory."""
        # Add the concept
        semantic_memory.add(sample_concept)

        # Remove the concept
        result = semantic_memory.remove(sample_concept.id)

        # Check that the concept was removed
        assert result is True
        assert sample_concept.id not in semantic_memory.items

    def test_remove_nonexistent_concept(self, semantic_memory):
        """Test removing a nonexistent concept from semantic memory."""
        # Remove a nonexistent concept
        result = semantic_memory.remove("nonexistent")

        # Check that False was returned
        assert result is False

    def test_clear_concepts(self, semantic_memory, sample_concept):
        """Test clearing all concepts from semantic memory."""
        # Add the concept
        semantic_memory.add(sample_concept)

        # Clear the memory
        semantic_memory.clear()

        # Check that the memory is empty
        assert len(semantic_memory.items) == 0

    def test_add_relation(self, semantic_memory, sample_concepts):
        """Test adding a relation between concepts."""
        # Add a relation
        relation_id = semantic_memory.add_relation(
            sample_concepts["dog"],
            sample_concepts["animal"],
            RelationType.IS_A,
            metadata={"confidence": 0.9},
            weight=0.8
        )

        # Check that the relation was added
        assert relation_id is not None

        # Get the source concept
        dog_concept = semantic_memory.get(sample_concepts["dog"])

        # Check that the relation is in the source concept
        assert relation_id in dog_concept.relations
        assert dog_concept.relations[relation_id].source_id == sample_concepts["dog"]
        assert dog_concept.relations[relation_id].target_id == sample_concepts["animal"]
        assert dog_concept.relations[relation_id].relation_type == RelationType.IS_A
        assert dog_concept.relations[relation_id].metadata == {"confidence": 0.9}
        assert dog_concept.relations[relation_id].weight == 0.8

    def test_add_relation_nonexistent_concept(self, semantic_memory, sample_concepts):
        """Test adding a relation with a nonexistent concept."""
        # Add a relation with a nonexistent source
        relation_id = semantic_memory.add_relation(
            "nonexistent",
            sample_concepts["animal"],
            RelationType.IS_A
        )

        # Check that None was returned
        assert relation_id is None

        # Add a relation with a nonexistent target
        relation_id = semantic_memory.add_relation(
            sample_concepts["dog"],
            "nonexistent",
            RelationType.IS_A
        )

        # Check that None was returned
        assert relation_id is None

    def test_get_relation(self, semantic_memory, sample_concepts):
        """Test getting a relation from a concept."""
        # Add a relation
        relation_id = semantic_memory.add_relation(
            sample_concepts["dog"],
            sample_concepts["animal"],
            RelationType.IS_A
        )

        # Get the relation
        relation = semantic_memory.get_relation(sample_concepts["dog"], relation_id)

        # Check that the correct relation was retrieved
        assert relation.id == relation_id
        assert relation.source_id == sample_concepts["dog"]
        assert relation.target_id == sample_concepts["animal"]
        assert relation.relation_type == RelationType.IS_A

    def test_get_nonexistent_relation(self, semantic_memory, sample_concepts):
        """Test getting a nonexistent relation from a concept."""
        # Get a nonexistent relation
        relation = semantic_memory.get_relation(sample_concepts["dog"], "nonexistent")

        # Check that None was returned
        assert relation is None

    def test_get_relation_nonexistent_concept(self, semantic_memory):
        """Test getting a relation from a nonexistent concept."""
        # Get a relation from a nonexistent concept
        relation = semantic_memory.get_relation("nonexistent", "nonexistent")

        # Check that None was returned
        assert relation is None

    def test_remove_relation(self, semantic_memory, sample_concepts):
        """Test removing a relation from a concept."""
        # Add a relation
        relation_id = semantic_memory.add_relation(
            sample_concepts["dog"],
            sample_concepts["animal"],
            RelationType.IS_A
        )

        # Remove the relation
        result = semantic_memory.remove_relation(sample_concepts["dog"], relation_id)

        # Check that the relation was removed
        assert result is True

        # Get the source concept
        dog_concept = semantic_memory.get(sample_concepts["dog"])

        # Check that the relation is not in the source concept
        assert relation_id not in dog_concept.relations

    def test_remove_nonexistent_relation(self, semantic_memory, sample_concepts):
        """Test removing a nonexistent relation from a concept."""
        # Remove a nonexistent relation
        result = semantic_memory.remove_relation(sample_concepts["dog"], "nonexistent")

        # Check that False was returned
        assert result is False

    def test_remove_relation_nonexistent_concept(self, semantic_memory):
        """Test removing a relation from a nonexistent concept."""
        # Remove a relation from a nonexistent concept
        result = semantic_memory.remove_relation("nonexistent", "nonexistent")

        # Check that False was returned
        assert result is False

    def test_get_relations_between(self, semantic_memory, sample_concepts):
        """Test getting relations between two concepts."""
        # Add relations in both directions
        relation1_id = semantic_memory.add_relation(
            sample_concepts["dog"],
            sample_concepts["animal"],
            RelationType.IS_A
        )

        relation2_id = semantic_memory.add_relation(
            sample_concepts["animal"],
            sample_concepts["dog"],
            RelationType.SUPERCLASS_OF
        )

        # Get relations between the concepts
        relations = semantic_memory.get_relations_between(
            sample_concepts["dog"],
            sample_concepts["animal"]
        )

        # Check that both relations were retrieved
        assert len(relations) == 2
        assert any(relation.id == relation1_id for relation in relations)
        assert any(relation.id == relation2_id for relation in relations)

    def test_get_relations_between_nonexistent_concept(self, semantic_memory, sample_concepts):
        """Test getting relations between a nonexistent concept."""
        # Get relations with a nonexistent concept
        relations = semantic_memory.get_relations_between(
            sample_concepts["dog"],
            "nonexistent"
        )

        # Check that an empty list was returned
        assert relations == []

        # Get relations with both nonexistent concepts
        relations = semantic_memory.get_relations_between(
            "nonexistent1",
            "nonexistent2"
        )

        # Check that an empty list was returned
        assert relations == []

    def test_add_attribute(self, semantic_memory, sample_concept):
        """Test adding an attribute to a concept."""
        # Add the concept
        semantic_memory.add(sample_concept)

        # Add an attribute
        result = semantic_memory.add_attribute(
            sample_concept.id,
            "new_attribute",
            "new_value"
        )

        # Check that the attribute was added
        assert result is True
        assert sample_concept.attributes["new_attribute"] == "new_value"

    def test_add_attribute_nonexistent_concept(self, semantic_memory):
        """Test adding an attribute to a nonexistent concept."""
        # Add an attribute to a nonexistent concept
        result = semantic_memory.add_attribute(
            "nonexistent",
            "attribute",
            "value"
        )

        # Check that False was returned
        assert result is False

    def test_remove_attribute(self, semantic_memory, sample_concept):
        """Test removing an attribute from a concept."""
        # Add the concept
        semantic_memory.add(sample_concept)

        # Remove an attribute
        result = semantic_memory.remove_attribute(
            sample_concept.id,
            "attribute1"
        )

        # Check that the attribute was removed
        assert result is True
        assert "attribute1" not in sample_concept.attributes

    def test_remove_nonexistent_attribute(self, semantic_memory, sample_concept):
        """Test removing a nonexistent attribute from a concept."""
        # Add the concept
        semantic_memory.add(sample_concept)

        # Remove a nonexistent attribute
        result = semantic_memory.remove_attribute(
            sample_concept.id,
            "nonexistent"
        )

        # Check that False was returned
        assert result is False

    def test_remove_attribute_nonexistent_concept(self, semantic_memory):
        """Test removing an attribute from a nonexistent concept."""
        # Remove an attribute from a nonexistent concept
        result = semantic_memory.remove_attribute(
            "nonexistent",
            "attribute"
        )

        # Check that False was returned
        assert result is False

    def test_add_example(self, semantic_memory, sample_concept):
        """Test adding an example to a concept."""
        # Add the concept
        semantic_memory.add(sample_concept)

        # Add an example
        result = semantic_memory.add_example(
            sample_concept.id,
            "new_example"
        )

        # Check that the example was added
        assert result is True
        assert "new_example" in sample_concept.examples

    def test_add_example_nonexistent_concept(self, semantic_memory):
        """Test adding an example to a nonexistent concept."""
        # Add an example to a nonexistent concept
        result = semantic_memory.add_example(
            "nonexistent",
            "example"
        )

        # Check that False was returned
        assert result is False

    def test_remove_example(self, semantic_memory, sample_concept):
        """Test removing an example from a concept."""
        # Add the concept
        semantic_memory.add(sample_concept)

        # Remove an example
        result = semantic_memory.remove_example(
            sample_concept.id,
            "example1"
        )

        # Check that the example was removed
        assert result is True
        assert "example1" not in sample_concept.examples

    def test_remove_nonexistent_example(self, semantic_memory, sample_concept):
        """Test removing a nonexistent example from a concept."""
        # Add the concept
        semantic_memory.add(sample_concept)

        # Remove a nonexistent example
        result = semantic_memory.remove_example(
            sample_concept.id,
            "nonexistent"
        )

        # Check that False was returned
        assert result is False

    def test_remove_example_nonexistent_concept(self, semantic_memory):
        """Test removing an example from a nonexistent concept."""
        # Remove an example from a nonexistent concept
        result = semantic_memory.remove_example(
            "nonexistent",
            "example"
        )

        # Check that False was returned
        assert result is False

    def test_search_by_name(self, semantic_memory, sample_concepts):
        """Test searching for concepts by name."""
        # Search for concepts
        results = semantic_memory.search("dog")

        # Check that the correct concepts were found
        # Note: Both "Dog" concept and "Animal" concept (which has "Dog" in examples) are found
        assert len(results) == 2
        assert any(concept.name == "Dog" for concept in results)
        assert any(concept.name == "Animal" for concept in results)

    def test_search_by_attribute(self, semantic_memory, sample_concepts):
        """Test searching for concepts by attribute."""
        # Search for concepts by attribute
        results = semantic_memory.search({"type": "mammal"})

        # Check that the correct concept was found
        assert len(results) == 1
        assert results[0].name == "Dog"

    def test_search_with_limit(self, semantic_memory, sample_concepts):
        """Test searching for concepts with a limit."""
        # Add another concept with "animal" in the name
        concept3 = Concept(
            name="Animal Behavior",
            description="The study of animal behavior",
            content="Animal behavior is the study of how animals interact with each other and their environment."
        )
        semantic_memory.add(concept3)

        # Search for concepts with a limit of 1
        results = semantic_memory.search("animal", limit=1)

        # Check that only one concept was returned
        assert len(results) == 1
        assert results[0].name in ["Animal", "Animal Behavior"]

    def test_concept_to_dict(self, sample_concept):
        """Test converting a concept to a dictionary."""
        # Add a relation to the concept
        relation = Relation(
            source_id=sample_concept.id,
            target_id="target_id",
            relation_type=RelationType.IS_A
        )
        sample_concept.add_relation(relation)

        # Convert the concept to a dictionary
        concept_dict = sample_concept.to_dict()

        # Check the dictionary
        assert concept_dict["id"] == sample_concept.id
        assert concept_dict["name"] == "Test Concept"
        assert concept_dict["description"] == "A test concept"
        assert concept_dict["content"] == "Test content"
        assert concept_dict["attributes"] == {"attribute1": "value1", "attribute2": "value2"}
        assert concept_dict["examples"] == ["example1", "example2"]
        assert "created_at" in concept_dict
        assert "updated_at" in concept_dict
        assert "relations" in concept_dict
        assert relation.id in concept_dict["relations"]

    def test_concept_from_dict(self):
        """Test creating a concept from a dictionary."""
        # Create a dictionary
        concept_dict = {
            "id": "test_id",
            "name": "Test Concept",
            "description": "A test concept",
            "content": "Test content",
            "attributes": {"attribute1": "value1", "attribute2": "value2"},
            "examples": ["example1", "example2"],
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "relations": {
                "relation1": {
                    "id": "relation1",
                    "source_id": "test_id",
                    "target_id": "target_id",
                    "relation_type": "IS_A",
                    "metadata": {"key": "value"},
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00",
                    "weight": 0.8
                }
            }
        }

        # Create a concept from the dictionary
        concept = Concept.from_dict(concept_dict)

        # Check the concept
        assert concept.id == "test_id"
        assert concept.name == "Test Concept"
        assert concept.description == "A test concept"
        assert concept.content == "Test content"
        assert concept.attributes == {"attribute1": "value1", "attribute2": "value2"}
        assert concept.examples == ["example1", "example2"]
        assert concept.created_at == "2023-01-01T00:00:00"
        assert concept.updated_at == "2023-01-01T00:00:00"
        assert "relation1" in concept.relations
        assert concept.relations["relation1"].source_id == "test_id"
        assert concept.relations["relation1"].target_id == "target_id"
        assert concept.relations["relation1"].relation_type == RelationType.IS_A
        assert concept.relations["relation1"].metadata == {"key": "value"}
        assert concept.relations["relation1"].weight == 0.8

    def test_relation_to_dict(self):
        """Test converting a relation to a dictionary."""
        # Create a relation
        relation = Relation(
            id="test_id",
            source_id="source_id",
            target_id="target_id",
            relation_type=RelationType.IS_A,
            metadata={"key": "value"},
            created_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00",
            weight=0.8
        )

        # Convert the relation to a dictionary
        relation_dict = relation.to_dict()

        # Check the dictionary
        assert relation_dict["id"] == "test_id"
        assert relation_dict["source_id"] == "source_id"
        assert relation_dict["target_id"] == "target_id"
        assert relation_dict["relation_type"] == "IS_A"
        assert relation_dict["metadata"] == {"key": "value"}
        assert relation_dict["created_at"] == "2023-01-01T00:00:00"
        assert relation_dict["updated_at"] == "2023-01-01T00:00:00"
        assert relation_dict["weight"] == 0.8

    def test_relation_from_dict(self):
        """Test creating a relation from a dictionary."""
        # Create a dictionary
        relation_dict = {
            "id": "test_id",
            "source_id": "source_id",
            "target_id": "target_id",
            "relation_type": "IS_A",
            "metadata": {"key": "value"},
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "weight": 0.8
        }

        # Create a relation from the dictionary
        relation = Relation.from_dict(relation_dict)

        # Check the relation
        assert relation.id == "test_id"
        assert relation.source_id == "source_id"
        assert relation.target_id == "target_id"
        assert relation.relation_type == RelationType.IS_A
        assert relation.metadata == {"key": "value"}
        assert relation.created_at == "2023-01-01T00:00:00"
        assert relation.updated_at == "2023-01-01T00:00:00"
        assert relation.weight == 0.8

    def test_semantic_memory_to_dict(self, semantic_memory, sample_concept):
        """Test converting a semantic memory to a dictionary."""
        # Add the concept
        semantic_memory.add(sample_concept)

        # Convert the memory to a dictionary
        memory_dict = semantic_memory.to_dict()

        # Check the dictionary
        assert memory_dict["name"] == "test_semantic_memory"
        assert memory_dict["memory_type"] == "SEMANTIC"
        assert "items" in memory_dict
        assert sample_concept.id in memory_dict["items"]

    def test_semantic_memory_from_dict(self):
        """Test creating a semantic memory from a dictionary."""
        # Create a dictionary
        memory_dict = {
            "name": "test_memory",
            "memory_type": "SEMANTIC",
            "items": {
                "concept1": {
                    "id": "concept1",
                    "name": "Test Concept",
                    "description": "A test concept",
                    "content": "Test content",
                    "attributes": {"attribute1": "value1"},
                    "examples": ["example1"],
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00",
                    "relations": {}
                }
            },
            "metadata": {"test": "value"}
        }

        # Create a memory from the dictionary
        memory = SemanticMemory.from_dict(memory_dict)

        # Check the memory
        assert memory.name == "test_memory"
        assert memory.memory_type == MemoryType.SEMANTIC
        assert len(memory.items) == 1
        assert "concept1" in memory.items
        assert memory.items["concept1"].name == "Test Concept"
        assert memory.metadata == {"test": "value"}
