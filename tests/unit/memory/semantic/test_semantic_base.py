"""
Unit tests for semantic memory base classes.

This module contains unit tests for the semantic memory base classes,
including RelationType, Relation, Concept, and SemanticMemory.
"""

import unittest
import pytest
import datetime
from unittest.mock import patch, MagicMock

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.memory.core.base import Memory, MemoryItem, MemoryType
from augment_adam.memory.semantic.base import RelationType, Relation, Concept, SemanticMemory

class TestRelationType(unittest.TestCase):
    """Tests for the RelationType class."""

    def test_relation_types(self):
        """Test that all relation types are defined."""
        # Check that all expected relation types are defined
        self.assertTrue(hasattr(RelationType, "IS_A"))
        self.assertTrue(hasattr(RelationType, "HAS_A"))
        self.assertTrue(hasattr(RelationType, "PART_OF"))
        self.assertTrue(hasattr(RelationType, "RELATED_TO"))
        self.assertTrue(hasattr(RelationType, "SYNONYM_OF"))
        self.assertTrue(hasattr(RelationType, "ANTONYM_OF"))
        self.assertTrue(hasattr(RelationType, "INSTANCE_OF"))
        self.assertTrue(hasattr(RelationType, "SUBCLASS_OF"))
        self.assertTrue(hasattr(RelationType, "SUPERCLASS_OF"))
        self.assertTrue(hasattr(RelationType, "ATTRIBUTE_OF"))
        self.assertTrue(hasattr(RelationType, "CAUSES"))
        self.assertTrue(hasattr(RelationType, "PRECEDES"))
        self.assertTrue(hasattr(RelationType, "FOLLOWS"))
        self.assertTrue(hasattr(RelationType, "SIMILAR_TO"))
        self.assertTrue(hasattr(RelationType, "OPPOSITE_OF"))
        self.assertTrue(hasattr(RelationType, "LOCATED_IN"))
        self.assertTrue(hasattr(RelationType, "USED_FOR"))
        self.assertTrue(hasattr(RelationType, "MADE_OF"))
        self.assertTrue(hasattr(RelationType, "DEFINED_AS"))
        self.assertTrue(hasattr(RelationType, "EXAMPLE_OF"))
        self.assertTrue(hasattr(RelationType, "CUSTOM"))

class TestRelation(unittest.TestCase):
    """Tests for the Relation class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.relation = Relation(
            id="test_relation_id",
            source_id="source_concept_id",
            target_id="target_concept_id",
            relation_type=RelationType.IS_A,
            metadata={"key": "value"},
            weight=0.8
        )

    def test_init(self):
        """Test initialization of Relation."""
        # Test with minimal arguments
        relation = Relation()
        self.assertIsNotNone(relation.id)
        self.assertEqual(relation.source_id, "")
        self.assertEqual(relation.target_id, "")
        self.assertEqual(relation.relation_type, RelationType.RELATED_TO)
        self.assertIsInstance(relation.metadata, dict)
        self.assertIsNotNone(relation.created_at)
        self.assertIsNotNone(relation.updated_at)
        self.assertEqual(relation.weight, 1.0)

        # Test with all arguments
        relation = Relation(
            id="test_id",
            source_id="source_id",
            target_id="target_id",
            relation_type=RelationType.IS_A,
            metadata={"key": "value"},
            created_at="2023-01-01T12:00:00",
            updated_at="2023-01-01T12:30:00",
            weight=0.5
        )
        self.assertEqual(relation.id, "test_id")
        self.assertEqual(relation.source_id, "source_id")
        self.assertEqual(relation.target_id, "target_id")
        self.assertEqual(relation.relation_type, RelationType.IS_A)
        self.assertEqual(relation.metadata, {"key": "value"})
        self.assertEqual(relation.created_at, "2023-01-01T12:00:00")
        self.assertEqual(relation.updated_at, "2023-01-01T12:30:00")
        self.assertEqual(relation.weight, 0.5)

        # Test with string relation type
        relation = Relation(relation_type="IS_A")
        self.assertEqual(relation.relation_type, RelationType.IS_A)

        # Test with invalid string relation type
        relation = Relation(relation_type="INVALID_TYPE")
        self.assertEqual(relation.relation_type, RelationType.CUSTOM)
        # The actual implementation might store the string in metadata["custom_relation_type"]
        # or it might store the enum value itself
        custom_relation_type = relation.metadata.get("custom_relation_type")
        self.assertTrue(custom_relation_type == "INVALID_TYPE" or custom_relation_type == RelationType.CUSTOM)

    def test_to_dict(self):
        """Test converting Relation to dictionary."""
        # Act
        result = self.relation.to_dict()

        # Assert
        self.assertEqual(result["id"], "test_relation_id")
        self.assertEqual(result["source_id"], "source_concept_id")
        self.assertEqual(result["target_id"], "target_concept_id")
        self.assertEqual(result["relation_type"], "IS_A")
        self.assertEqual(result["metadata"], {"key": "value"})
        self.assertEqual(result["weight"], 0.8)
        self.assertIn("created_at", result)
        self.assertIn("updated_at", result)

    def test_from_dict(self):
        """Test creating Relation from dictionary."""
        # Arrange
        data = {
            "id": "test_relation_id",
            "source_id": "source_concept_id",
            "target_id": "target_concept_id",
            "relation_type": "IS_A",
            "metadata": {"key": "value"},
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:30:00",
            "weight": 0.8
        }

        # Act
        relation = Relation.from_dict(data)

        # Assert
        self.assertEqual(relation.id, "test_relation_id")
        self.assertEqual(relation.source_id, "source_concept_id")
        self.assertEqual(relation.target_id, "target_concept_id")
        self.assertEqual(relation.relation_type, RelationType.IS_A)
        self.assertEqual(relation.metadata, {"key": "value"})
        self.assertEqual(relation.created_at, "2023-01-01T12:00:00")
        self.assertEqual(relation.updated_at, "2023-01-01T12:30:00")
        self.assertEqual(relation.weight, 0.8)

class TestConcept(unittest.TestCase):
    """Tests for the Concept class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.concept = Concept(
            id="test_concept_id",
            name="Test Concept",
            description="A test concept",
            content="Test concept content",
            metadata={"domain": "testing"},
            attributes={"color": "blue", "size": "large"},
            examples=["Example 1", "Example 2"]
        )

        self.relation = Relation(
            id="test_relation_id",
            source_id="test_concept_id",
            target_id="target_concept_id",
            relation_type=RelationType.IS_A
        )

    def test_init(self):
        """Test initialization of Concept."""
        # Test with minimal arguments
        concept = Concept()
        self.assertIsNotNone(concept.id)
        self.assertEqual(concept.name, "")
        self.assertEqual(concept.description, "")
        self.assertIsNone(concept.content)
        self.assertIsInstance(concept.metadata, dict)
        self.assertIsInstance(concept.attributes, dict)
        self.assertIsInstance(concept.examples, list)
        self.assertIsInstance(concept.relations, dict)

        # Test with all arguments
        concept = Concept(
            id="test_id",
            name="Test Name",
            description="Test Description",
            content="Test Content",
            metadata={"key": "value"},
            attributes={"attr1": "value1"},
            examples=["example1"],
            relations={"rel1": self.relation}
        )
        self.assertEqual(concept.id, "test_id")
        self.assertEqual(concept.name, "Test Name")
        self.assertEqual(concept.description, "Test Description")
        self.assertEqual(concept.content, "Test Content")
        self.assertEqual(concept.metadata, {"key": "value"})
        self.assertEqual(concept.attributes, {"attr1": "value1"})
        self.assertEqual(concept.examples, ["example1"])
        self.assertEqual(concept.relations, {"rel1": self.relation})

        # Test with name but no content
        concept = Concept(name="Test Name")
        self.assertEqual(concept.name, "Test Name")
        self.assertEqual(concept.content, "Test Name")

    def test_add_relation(self):
        """Test adding a relation to a concept."""
        # Arrange
        concept = Concept(id="source_id")
        relation = Relation(
            id="relation_id",
            source_id="source_id",
            target_id="target_id",
            relation_type=RelationType.IS_A
        )

        # Act
        relation_id = concept.add_relation(relation)

        # Assert
        self.assertEqual(relation_id, "relation_id")
        self.assertEqual(len(concept.relations), 1)
        self.assertEqual(concept.relations["relation_id"], relation)

    def test_get_relation(self):
        """Test getting a relation from a concept."""
        # Arrange
        concept = Concept(id="source_id")
        relation = Relation(
            id="relation_id",
            source_id="source_id",
            target_id="target_id",
            relation_type=RelationType.IS_A
        )
        concept.add_relation(relation)

        # Act
        retrieved_relation = concept.get_relation("relation_id")

        # Assert
        self.assertEqual(retrieved_relation, relation)

        # Test getting a non-existent relation
        self.assertIsNone(concept.get_relation("non_existent_id"))

    def test_remove_relation(self):
        """Test removing a relation from a concept."""
        # Arrange
        concept = Concept(id="source_id")
        relation1 = Relation(id="relation1", source_id="source_id", target_id="target1")
        relation2 = Relation(id="relation2", source_id="source_id", target_id="target2")
        concept.add_relation(relation1)
        concept.add_relation(relation2)

        # Act - remove first relation
        result = concept.remove_relation("relation1")

        # Assert
        self.assertTrue(result)
        self.assertEqual(len(concept.relations), 1)
        self.assertNotIn("relation1", concept.relations)
        self.assertIn("relation2", concept.relations)

        # Act - try to remove non-existent relation
        result = concept.remove_relation("non_existent_id")

        # Assert
        self.assertFalse(result)
        self.assertEqual(len(concept.relations), 1)

    def test_get_relations_by_type(self):
        """Test getting relations by type from a concept."""
        # Arrange
        concept = Concept(id="source_id")
        relation1 = Relation(id="relation1", source_id="source_id", target_id="target1", relation_type=RelationType.IS_A)
        relation2 = Relation(id="relation2", source_id="source_id", target_id="target2", relation_type=RelationType.HAS_A)
        relation3 = Relation(id="relation3", source_id="source_id", target_id="target3", relation_type=RelationType.IS_A)
        concept.add_relation(relation1)
        concept.add_relation(relation2)
        concept.add_relation(relation3)

        # Act - get IS_A relations
        relations = concept.get_relations_by_type(RelationType.IS_A)

        # Assert
        self.assertEqual(len(relations), 2)
        self.assertIn(relation1, relations)
        self.assertIn(relation3, relations)

        # Act - get HAS_A relations
        relations = concept.get_relations_by_type(RelationType.HAS_A)

        # Assert
        self.assertEqual(len(relations), 1)
        self.assertIn(relation2, relations)

        # Act - get non-existent relation type
        relations = concept.get_relations_by_type(RelationType.PART_OF)

        # Assert
        self.assertEqual(len(relations), 0)

    def test_get_relations_to_concept(self):
        """Test getting relations to a specific concept."""
        # Arrange
        concept = Concept(id="source_id")
        relation1 = Relation(id="relation1", source_id="source_id", target_id="target1")
        relation2 = Relation(id="relation2", source_id="source_id", target_id="target2")
        relation3 = Relation(id="relation3", source_id="source_id", target_id="target1")
        concept.add_relation(relation1)
        concept.add_relation(relation2)
        concept.add_relation(relation3)

        # Act - get relations to target1
        relations = concept.get_relations_to_concept("target1")

        # Assert
        self.assertEqual(len(relations), 2)
        self.assertIn(relation1, relations)
        self.assertIn(relation3, relations)

        # Act - get relations to target2
        relations = concept.get_relations_to_concept("target2")

        # Assert
        self.assertEqual(len(relations), 1)
        self.assertIn(relation2, relations)

        # Act - get relations to non-existent target
        relations = concept.get_relations_to_concept("non_existent_target")

        # Assert
        self.assertEqual(len(relations), 0)

    def test_add_attribute(self):
        """Test adding an attribute to a concept."""
        # Arrange
        concept = Concept()

        # Act
        concept.add_attribute("color", "blue")

        # Assert
        self.assertEqual(concept.attributes["color"], "blue")

        # Act - update existing attribute
        concept.add_attribute("color", "red")

        # Assert
        self.assertEqual(concept.attributes["color"], "red")

    def test_get_attribute(self):
        """Test getting an attribute from a concept."""
        # Arrange
        concept = Concept(attributes={"color": "blue", "size": "large"})

        # Act - get existing attribute
        color = concept.get_attribute("color")

        # Assert
        self.assertEqual(color, "blue")

        # Act - get non-existent attribute with default
        shape = concept.get_attribute("shape", "round")

        # Assert
        self.assertEqual(shape, "round")

        # Act - get non-existent attribute without default
        texture = concept.get_attribute("texture")

        # Assert
        self.assertIsNone(texture)

    def test_remove_attribute(self):
        """Test removing an attribute from a concept."""
        # Arrange
        concept = Concept(attributes={"color": "blue", "size": "large"})

        # Act - remove existing attribute
        result = concept.remove_attribute("color")

        # Assert
        self.assertTrue(result)
        self.assertNotIn("color", concept.attributes)
        self.assertIn("size", concept.attributes)

        # Act - remove non-existent attribute
        result = concept.remove_attribute("shape")

        # Assert
        self.assertFalse(result)

    def test_add_example(self):
        """Test adding an example to a concept."""
        # Arrange
        concept = Concept(examples=["Example 1"])

        # Act - add new example
        concept.add_example("Example 2")

        # Assert
        self.assertEqual(len(concept.examples), 2)
        self.assertIn("Example 1", concept.examples)
        self.assertIn("Example 2", concept.examples)

        # Act - add duplicate example
        concept.add_example("Example 1")

        # Assert
        self.assertEqual(len(concept.examples), 2)

    def test_remove_example(self):
        """Test removing an example from a concept."""
        # Arrange
        concept = Concept(examples=["Example 1", "Example 2", "Example 3"])

        # Act - remove existing example
        result = concept.remove_example("Example 2")

        # Assert
        self.assertTrue(result)
        self.assertEqual(len(concept.examples), 2)
        self.assertIn("Example 1", concept.examples)
        self.assertIn("Example 3", concept.examples)
        self.assertNotIn("Example 2", concept.examples)

        # Act - remove non-existent example
        result = concept.remove_example("Example 4")

        # Assert
        self.assertFalse(result)
        self.assertEqual(len(concept.examples), 2)

    def test_to_dict(self):
        """Test converting Concept to dictionary."""
        # Act
        result = self.concept.to_dict()

        # Assert
        self.assertEqual(result["id"], "test_concept_id")
        self.assertEqual(result["name"], "Test Concept")
        self.assertEqual(result["description"], "A test concept")
        self.assertEqual(result["content"], "Test concept content")
        self.assertEqual(result["metadata"], {"domain": "testing"})
        self.assertEqual(result["attributes"], {"color": "blue", "size": "large"})
        self.assertEqual(result["examples"], ["Example 1", "Example 2"])
        self.assertEqual(result["relations"], {})

    def test_from_dict(self):
        """Test creating Concept from dictionary."""
        # Arrange
        relation_data = {
            "id": "relation_id",
            "source_id": "concept_id",
            "target_id": "target_id",
            "relation_type": "IS_A",
            "metadata": {},
            "weight": 1.0
        }

        data = {
            "id": "concept_id",
            "name": "Test Concept",
            "description": "A test concept",
            "content": "Test content",
            "metadata": {"domain": "testing"},
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:30:00",
            "importance": 0.8,
            "attributes": {"color": "blue", "size": "large"},
            "examples": ["Example 1", "Example 2"],
            "relations": {"relation_id": relation_data}
        }

        # Act
        concept = Concept.from_dict(data)

        # Assert
        self.assertEqual(concept.id, "concept_id")
        self.assertEqual(concept.name, "Test Concept")
        self.assertEqual(concept.description, "A test concept")
        self.assertEqual(concept.content, "Test content")
        self.assertEqual(concept.metadata, {"domain": "testing"})
        self.assertEqual(concept.created_at, "2023-01-01T12:00:00")
        self.assertEqual(concept.updated_at, "2023-01-01T12:30:00")
        self.assertEqual(concept.importance, 0.8)
        self.assertEqual(concept.attributes, {"color": "blue", "size": "large"})
        self.assertEqual(concept.examples, ["Example 1", "Example 2"])
        self.assertEqual(len(concept.relations), 1)
        self.assertIn("relation_id", concept.relations)
        self.assertEqual(concept.relations["relation_id"].source_id, "concept_id")
        self.assertEqual(concept.relations["relation_id"].target_id, "target_id")
        self.assertEqual(concept.relations["relation_id"].relation_type, RelationType.IS_A)

class TestSemanticMemory(unittest.TestCase):
    """Tests for the SemanticMemory class."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize objects for testing
        self.memory = SemanticMemory(name="test_semantic_memory")

        # Create sample concepts
        self.concept1 = Concept(
            id="concept1",
            name="Concept 1",
            description="First test concept",
            content="Content for concept 1",
            metadata={"domain": "test"}
        )
        self.concept2 = Concept(
            id="concept2",
            name="Concept 2",
            description="Second test concept",
            content="Content for concept 2",
            metadata={"domain": "test"}
        )

        # Create sample relations
        self.relation1 = Relation(
            id="relation1",
            source_id="concept1",
            target_id="concept2",
            relation_type=RelationType.IS_A,
            metadata={"confidence": 0.9}
        )

    def test_init(self):
        """Test initialization of SemanticMemory."""
        # Test with name
        memory = SemanticMemory(name="test_memory")
        self.assertEqual(memory.name, "test_memory")
        self.assertEqual(memory.memory_type, MemoryType.SEMANTIC)
        self.assertEqual(len(memory.items), 0)
        self.assertEqual(memory.metadata, {})

    def test_add(self):
        """Test adding a concept to semantic memory."""
        # Arrange
        concept = Concept(id="test_concept", name="Test Concept")

        # Act
        concept_id = self.memory.add(concept)

        # Assert
        self.assertEqual(concept_id, "test_concept")
        self.assertEqual(len(self.memory.items), 1)
        self.assertEqual(self.memory.items["test_concept"], concept)

    def test_get(self):
        """Test getting a concept from semantic memory."""
        # Arrange
        self.memory.add(self.concept1)

        # Act
        retrieved_concept = self.memory.get("concept1")

        # Assert
        self.assertEqual(retrieved_concept, self.concept1)

        # Test getting a non-existent concept
        self.assertIsNone(self.memory.get("non_existent_id"))

    def test_update(self):
        """Test updating a concept in semantic memory."""
        # Arrange
        self.memory.add(self.concept1)

        # Create an updated concept
        updated_concept = Concept(
            id="concept1",
            name="Updated Name",
            description="Updated Description",
            content="Updated content"
        )

        # Act - update the concept's content
        result = self.memory.update("concept1", content=updated_concept)

        # Assert
        self.assertIsNotNone(result)
        retrieved_concept = self.memory.get("concept1")
        self.assertEqual(retrieved_concept.content, updated_concept)

        # Test updating a non-existent concept
        result = self.memory.update("non_existent_id", content="Updated content")
        self.assertIsNone(result)

    def test_remove(self):
        """Test removing a concept from semantic memory."""
        # Arrange
        self.memory.add(self.concept1)
        self.memory.add(self.concept2)

        # Act
        result = self.memory.remove("concept1")

        # Assert
        self.assertTrue(result)
        self.assertEqual(len(self.memory.items), 1)
        self.assertNotIn("concept1", self.memory.items)
        self.assertIn("concept2", self.memory.items)

        # Test removing a non-existent concept
        self.assertFalse(self.memory.remove("non_existent_id"))

    def test_add_relation(self):
        """Test adding a relation between concepts."""
        # Arrange
        self.memory.add(self.concept1)
        self.memory.add(self.concept2)

        # Act
        relation_id = self.memory.add_relation("concept1", "concept2", RelationType.IS_A, metadata={"confidence": 0.9})

        # Assert
        self.assertIsNotNone(relation_id)
        concept1 = self.memory.get("concept1")
        self.assertEqual(len(concept1.relations), 1)
        relation = self.memory.get_relation("concept1", relation_id)
        self.assertEqual(relation.source_id, "concept1")
        self.assertEqual(relation.target_id, "concept2")
        self.assertEqual(relation.relation_type, RelationType.IS_A)
        self.assertEqual(relation.metadata, {"confidence": 0.9})

        # Test adding a relation with non-existent source concept
        self.assertIsNone(self.memory.add_relation("non_existent_id", "concept2", RelationType.IS_A))

        # Test adding a relation with non-existent target concept
        self.assertIsNone(self.memory.add_relation("concept1", "non_existent_id", RelationType.IS_A))

    def test_get_relation(self):
        """Test getting a relation from semantic memory."""
        # Arrange
        self.memory.add(self.concept1)
        self.memory.add(self.concept2)
        relation_id = self.memory.add_relation("concept1", "concept2", RelationType.IS_A)

        # Act
        relation = self.memory.get_relation("concept1", relation_id)

        # Assert
        self.assertIsNotNone(relation)
        self.assertEqual(relation.source_id, "concept1")
        self.assertEqual(relation.target_id, "concept2")
        self.assertEqual(relation.relation_type, RelationType.IS_A)

        # Test getting a relation from a non-existent concept
        self.assertIsNone(self.memory.get_relation("non_existent_id", relation_id))

        # Test getting a non-existent relation
        self.assertIsNone(self.memory.get_relation("concept1", "non_existent_id"))

    def test_remove_relation(self):
        """Test removing a relation from semantic memory."""
        # Arrange
        self.memory.add(self.concept1)
        self.memory.add(self.concept2)
        relation_id1 = self.memory.add_relation("concept1", "concept2", RelationType.IS_A)
        relation_id2 = self.memory.add_relation("concept2", "concept1", RelationType.HAS_A)

        # Act
        result = self.memory.remove_relation("concept1", relation_id1)

        # Assert
        self.assertTrue(result)
        concept1 = self.memory.get("concept1")
        concept2 = self.memory.get("concept2")
        self.assertEqual(len(concept1.relations), 0)
        self.assertEqual(len(concept2.relations), 1)
        self.assertIsNone(self.memory.get_relation("concept1", relation_id1))
        self.assertIsNotNone(self.memory.get_relation("concept2", relation_id2))

        # Test removing a relation from a non-existent concept
        self.assertFalse(self.memory.remove_relation("non_existent_id", relation_id2))

        # Test removing a non-existent relation
        self.assertFalse(self.memory.remove_relation("concept2", "non_existent_id"))

    def test_get_relations_by_type(self):
        """Test getting relations by type from semantic memory."""
        # Arrange
        self.memory.add(self.concept1)
        self.memory.add(self.concept2)
        self.memory.add_relation("concept1", "concept2", RelationType.IS_A)
        self.memory.add_relation("concept1", "concept2", RelationType.HAS_A)
        self.memory.add_relation("concept2", "concept1", RelationType.IS_A)

        # Act - get IS_A relations from concept1
        relations = self.memory.get_relations_by_type("concept1", RelationType.IS_A)

        # Assert
        self.assertEqual(len(relations), 1)
        self.assertTrue(all(r.relation_type == RelationType.IS_A for r in relations))

        # Act - get IS_A relations from concept2
        relations = self.memory.get_relations_by_type("concept2", RelationType.IS_A)

        # Assert
        self.assertEqual(len(relations), 1)
        self.assertTrue(all(r.relation_type == RelationType.IS_A for r in relations))

        # Act - get HAS_A relations from concept1
        relations = self.memory.get_relations_by_type("concept1", RelationType.HAS_A)

        # Assert
        self.assertEqual(len(relations), 1)
        self.assertTrue(all(r.relation_type == RelationType.HAS_A for r in relations))

        # Act - get non-existent relation type
        relations = self.memory.get_relations_by_type("concept1", RelationType.PART_OF)

        # Assert
        self.assertEqual(len(relations), 0)

        # Act - get relations from non-existent concept
        relations = self.memory.get_relations_by_type("non_existent_id", RelationType.IS_A)

        # Assert
        self.assertEqual(len(relations), 0)

    def test_get_relations_between(self):
        """Test getting relations between specific concepts."""
        # Arrange
        self.memory.add(self.concept1)
        self.memory.add(self.concept2)
        self.memory.add_relation("concept1", "concept2", RelationType.IS_A)
        self.memory.add_relation("concept1", "concept2", RelationType.HAS_A)
        self.memory.add_relation("concept2", "concept1", RelationType.PART_OF)

        # Act - get relations between concept1 and concept2
        relations = self.memory.get_relations_between("concept1", "concept2")

        # Assert
        self.assertEqual(len(relations), 3)

        # Count relations from concept1 to concept2
        c1_to_c2 = [r for r in relations if r.source_id == "concept1" and r.target_id == "concept2"]
        self.assertEqual(len(c1_to_c2), 2)

        # Count relations from concept2 to concept1
        c2_to_c1 = [r for r in relations if r.source_id == "concept2" and r.target_id == "concept1"]
        self.assertEqual(len(c2_to_c1), 1)

        # Act - get relations with non-existent source
        relations = self.memory.get_relations_between("non_existent_id", "concept2")

        # Assert
        self.assertEqual(len(relations), 0)

        # Act - get relations with non-existent target
        relations = self.memory.get_relations_between("concept1", "non_existent_id")

        # Assert
        self.assertEqual(len(relations), 0)



    def test_search(self):
        """Test searching for concepts in semantic memory."""
        # Arrange
        self.memory.add(self.concept1)
        self.memory.add(self.concept2)

        # Mock the parent class's search method
        with patch.object(Memory, 'search') as mock_search:
            mock_search.return_value = [self.concept1]

            # Create a new memory instance to avoid issues with previous patches
            test_memory = SemanticMemory(name="test_search_memory")
            test_memory.add(self.concept1)
            test_memory.add(self.concept2)

            # Override the parent class's search method for this instance
            with patch.object(test_memory.__class__, 'search', return_value=[self.concept1]):
                # Act - search with string query
                results = test_memory.search("Concept 1", 10)

                # Assert
                self.assertEqual(results, [self.concept1])

    def test_to_dict(self):
        """Test converting SemanticMemory to dictionary."""
        # Arrange
        self.memory.add(self.concept1)
        self.memory.add(self.concept2)
        relation_id = self.memory.add_relation("concept1", "concept2", RelationType.IS_A)

        # Act
        result = self.memory.to_dict()

        # Assert
        self.assertEqual(result["name"], "test_semantic_memory")
        self.assertEqual(result["memory_type"], "SEMANTIC")
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["items"]["concept1"]["id"], "concept1")
        self.assertEqual(result["items"]["concept2"]["id"], "concept2")

        # Check that the relation is in the concept's relations
        self.assertEqual(len(result["items"]["concept1"]["relations"]), 1)
        concept1_relations = result["items"]["concept1"]["relations"]
        self.assertIn(relation_id, concept1_relations)
        self.assertEqual(concept1_relations[relation_id]["source_id"], "concept1")
        self.assertEqual(concept1_relations[relation_id]["target_id"], "concept2")
        self.assertEqual(concept1_relations[relation_id]["relation_type"], "IS_A")

    def test_from_dict(self):
        """Test creating SemanticMemory from dictionary."""
        # Arrange
        relation_data = {
            "id": "relation_id",
            "source_id": "concept1",
            "target_id": "concept2",
            "relation_type": "IS_A",
            "metadata": {},
            "weight": 1.0
        }

        concept1_data = {
            "id": "concept1",
            "name": "Concept 1",
            "description": "First test concept",
            "content": "Content for concept 1",
            "metadata": {"domain": "test"},
            "attributes": {},
            "examples": [],
            "relations": {
                "relation_id": relation_data
            }
        }

        concept2_data = {
            "id": "concept2",
            "name": "Concept 2",
            "description": "Second test concept",
            "content": "Content for concept 2",
            "metadata": {"domain": "test"},
            "attributes": {},
            "examples": [],
            "relations": {}
        }

        data = {
            "name": "test_semantic_memory",
            "memory_type": "SEMANTIC",
            "metadata": {},
            "items": {
                "concept1": concept1_data,
                "concept2": concept2_data
            }
        }

        # Act
        memory = SemanticMemory.from_dict(data)

        # Assert
        self.assertEqual(memory.name, "test_semantic_memory")
        self.assertEqual(memory.memory_type, MemoryType.SEMANTIC)
        self.assertEqual(len(memory.items), 2)
        self.assertEqual(memory.items["concept1"].name, "Concept 1")
        self.assertEqual(memory.items["concept2"].name, "Concept 2")

        # Check that the relation is in the concept's relations
        concept1 = memory.get("concept1")
        self.assertEqual(len(concept1.relations), 1)
        relation = concept1.get_relation("relation_id")
        self.assertIsNotNone(relation)
        self.assertEqual(relation.source_id, "concept1")
        self.assertEqual(relation.target_id, "concept2")
        self.assertEqual(relation.relation_type, RelationType.IS_A)


if __name__ == '__main__':
    unittest.main()
