"""
Integration tests for the Memory systems.

This module contains integration tests for the Memory systems, including
interactions between different memory types.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from augment_adam.memory.core.base import MemoryType, MemoryManager
from augment_adam.memory.episodic.base import EpisodicMemory, Episode, Event
from augment_adam.memory.semantic.base import SemanticMemory, Concept, Relation, RelationType
from augment_adam.memory.graph.base import GraphMemory, GraphMemoryItem, Node, Edge, Relationship
from augment_adam.memory.working.base import WorkingMemory, WorkingMemoryItem


class TestMemoryIntegration:
    """Integration tests for the Memory systems."""

    @pytest.fixture
    def memory_manager(self):
        """Create a MemoryManager with all memory types for testing."""
        manager = MemoryManager()

        # Register memory systems
        manager.register_memory(WorkingMemory(name="working_memory"))
        manager.register_memory(EpisodicMemory(name="episodic_memory"))
        manager.register_memory(SemanticMemory(name="semantic_memory"))
        manager.register_memory(GraphMemory(name="graph_memory"))

        return manager

    def test_memory_manager_initialization(self, memory_manager):
        """Test initializing a MemoryManager with all memory types."""
        # Check that all memory systems were added
        assert len(memory_manager.memories) == 4
        assert memory_manager.get_memory("working_memory") is not None
        assert memory_manager.get_memory("episodic_memory") is not None
        assert memory_manager.get_memory("semantic_memory") is not None
        assert memory_manager.get_memory("graph_memory") is not None

        # Check memory types
        assert memory_manager.get_memory("working_memory").memory_type == MemoryType.WORKING
        assert memory_manager.get_memory("episodic_memory").memory_type == MemoryType.EPISODIC
        assert memory_manager.get_memory("semantic_memory").memory_type == MemoryType.SEMANTIC
        assert memory_manager.get_memory("graph_memory").memory_type == MemoryType.GRAPH

    def test_working_to_episodic_memory(self, memory_manager):
        """Test transferring information from working memory to episodic memory."""
        # Get memory systems
        working_memory = memory_manager.get_memory("working_memory")
        episodic_memory = memory_manager.get_memory("episodic_memory")

        # Create a working memory item
        working_item = WorkingMemoryItem(
            content="Meeting with Alice about the project",
            metadata={"importance": 0.8}
        )

        # Add the item to working memory
        working_memory.add(working_item)

        # Create an episode based on the working memory item
        episode = Episode(
            content=working_item.content,
            metadata=working_item.metadata
        )

        # Add events to the episode
        episode.add_event(Event(content="Discussed project timeline", metadata={"speaker": "Alice"}))
        episode.add_event(Event(content="Agreed on next steps", metadata={"speaker": "User"}))

        # Add the episode to episodic memory
        episodic_memory.add(episode)

        # Check that the episode was added
        retrieved_episode = episodic_memory.get(episode.id)
        assert retrieved_episode is not None
        assert retrieved_episode.content == "Meeting with Alice about the project"
        assert len(retrieved_episode.events) == 2

    def test_episodic_to_semantic_memory(self, memory_manager):
        """Test extracting semantic information from episodic memory."""
        # Get memory systems
        episodic_memory = memory_manager.get_memory("episodic_memory")
        semantic_memory = memory_manager.get_memory("semantic_memory")

        # Create an episode
        episode = Episode(
            content="Learning about Python programming",
            metadata={"topic": "programming"}
        )

        # Add events to the episode
        episode.add_event(Event(content="Python is a high-level programming language", metadata={"source": "book"}))
        episode.add_event(Event(content="Python supports multiple programming paradigms", metadata={"source": "lecture"}))

        # Add the episode to episodic memory
        episodic_memory.add(episode)

        # Create concepts based on the episode
        python_concept = Concept(
            name="Python",
            description="A high-level programming language",
            content="Python is a high-level programming language that supports multiple programming paradigms",
            attributes={"type": "programming_language", "level": "high-level"},
            examples=["Python 3.9", "Python 3.10"]
        )

        programming_concept = Concept(
            name="Programming",
            description="The process of creating computer software",
            content="Programming is the process of designing and building an executable computer program",
            attributes={"field": "computer_science"},
            examples=["Python programming", "Java programming"]
        )

        # Add concepts to semantic memory
        python_id = semantic_memory.add(python_concept)
        programming_id = semantic_memory.add(programming_concept)

        # Add relation between concepts
        semantic_memory.add_relation(
            python_id,
            programming_id,
            RelationType.IS_A,
            metadata={"confidence": 0.9}
        )

        # Check that the concepts were added
        retrieved_python = semantic_memory.get(python_id)
        retrieved_programming = semantic_memory.get(programming_id)

        assert retrieved_python is not None
        assert retrieved_programming is not None
        assert retrieved_python.name == "Python"
        assert retrieved_programming.name == "Programming"

        # Check that the relation was added
        relations = semantic_memory.get_relations_between(python_id, programming_id)
        assert len(relations) == 1
        assert relations[0].relation_type == RelationType.IS_A

    def test_semantic_to_graph_memory(self, memory_manager):
        """Test converting semantic information to graph representation."""
        # Get memory systems
        semantic_memory = memory_manager.get_memory("semantic_memory")
        graph_memory = memory_manager.get_memory("graph_memory")

        # Create concepts
        dog_concept = Concept(
            name="Dog",
            description="A domesticated carnivorous mammal",
            content="Dogs are domesticated mammals, not natural wild animals.",
            attributes={"type": "mammal", "domesticated": True},
            examples=["Labrador", "Poodle"]
        )

        animal_concept = Concept(
            name="Animal",
            description="A living organism that feeds on organic matter",
            content="Animals are multicellular eukaryotic organisms.",
            attributes={"type": "organism", "kingdom": "Animalia"},
            examples=["Dog", "Cat", "Elephant"]
        )

        # Add concepts to semantic memory
        dog_id = semantic_memory.add(dog_concept)
        animal_id = semantic_memory.add(animal_concept)

        # Add relation between concepts
        semantic_memory.add_relation(
            dog_id,
            animal_id,
            RelationType.IS_A,
            metadata={"confidence": 0.9}
        )

        # Create a graph representation
        graph_item = GraphMemoryItem(content="Animal taxonomy graph")

        # Create nodes from concepts
        dog_node = Node(
            labels=["Concept"],
            properties={
                "name": dog_concept.name,
                "description": dog_concept.description,
                "attributes": dog_concept.attributes
            }
        )

        animal_node = Node(
            labels=["Concept"],
            properties={
                "name": animal_concept.name,
                "description": animal_concept.description,
                "attributes": animal_concept.attributes
            }
        )

        # Add nodes to the graph
        dog_node_id = graph_item.add_node(dog_node)
        animal_node_id = graph_item.add_node(animal_node)

        # Create edge from relation
        edge = Edge(
            source_id=dog_node_id,
            target_id=animal_node_id,
            relationship=Relationship.RELATED_TO,
            properties={"type": "IS_A", "confidence": 0.9}
        )

        # Add edge to the graph
        graph_item.add_edge(edge)

        # Add the graph item to graph memory
        graph_memory.add(graph_item)

        # Check that the graph item was added
        retrieved_graph = graph_memory.get(graph_item.id)
        assert retrieved_graph is not None
        assert len(retrieved_graph.nodes) == 2
        assert len(retrieved_graph.edges) == 1

        # Check that the nodes and edge were added correctly
        assert any(node.properties["name"] == "Dog" for node in retrieved_graph.nodes.values())
        assert any(node.properties["name"] == "Animal" for node in retrieved_graph.nodes.values())

        # Get the edge
        edge_id = next(iter(retrieved_graph.edges))
        edge = retrieved_graph.edges[edge_id]

        # Check the edge properties
        assert edge.relationship == Relationship.RELATED_TO
        assert edge.properties["type"] == "IS_A"
        assert edge.properties["confidence"] == 0.9

    def test_cross_memory_query(self, memory_manager):
        """Test querying across multiple memory systems."""
        # Get memory systems
        working_memory = memory_manager.get_memory("working_memory")
        episodic_memory = memory_manager.get_memory("episodic_memory")
        semantic_memory = memory_manager.get_memory("semantic_memory")

        # Add items to working memory
        working_item = WorkingMemoryItem(
            content="Current task: Research Python libraries for data analysis",
            metadata={"priority": "high"}
        )
        working_memory.add(working_item)

        # Add items to episodic memory
        episode = Episode(
            content="Learning about Python data analysis libraries",
            metadata={"topic": "data_analysis"}
        )
        episode.add_event(Event(content="Pandas is a powerful data analysis library", metadata={"source": "tutorial"}))
        episode.add_event(Event(content="NumPy provides support for large arrays", metadata={"source": "documentation"}))
        episodic_memory.add(episode)

        # Add items to semantic memory
        pandas_concept = Concept(
            name="Pandas",
            description="A data analysis library for Python",
            content="Pandas is a software library written for data manipulation and analysis in Python",
            attributes={"language": "Python", "purpose": "data_analysis"},
            examples=["DataFrame", "Series"]
        )
        numpy_concept = Concept(
            name="NumPy",
            description="A library for scientific computing with Python",
            content="NumPy is a library for the Python programming language, adding support for large arrays",
            attributes={"language": "Python", "purpose": "scientific_computing"},
            examples=["ndarray", "vectorization"]
        )
        semantic_memory.add(pandas_concept)
        semantic_memory.add(numpy_concept)

        # Perform a cross-memory query for "Python data analysis"
        # In a real implementation, this would be a more sophisticated search

        # Search working memory
        working_results = [item for item in working_memory.items.values()
                          if "python" in item.content.lower() and "data analysis" in item.content.lower()]

        # Search episodic memory
        episodic_results = [item for item in episodic_memory.items.values()
                           if "python" in item.content.lower() and "data analysis" in item.content.lower()]

        # Search semantic memory - search by name and description
        semantic_results_name = semantic_memory.search("Pandas")
        semantic_results_desc = semantic_memory.search("data analysis")

        # Check results
        assert len(working_results) == 1
        assert "Research Python libraries for data analysis" in working_results[0].content

        assert len(episodic_results) == 1
        assert "Learning about Python data analysis libraries" in episodic_results[0].content

        # Check that we can find concepts by name
        assert len(semantic_results_name) == 1
        assert semantic_results_name[0].name == "Pandas"

        # Check that we can find concepts by description
        assert len(semantic_results_desc) == 1
        assert semantic_results_desc[0].name == "Pandas"

    def test_memory_persistence(self, memory_manager):
        """Test memory persistence across memory systems."""
        # This test simulates saving and loading memory systems
        # In a real implementation, this would involve serialization to disk

        # Get memory systems
        working_memory = memory_manager.get_memory("working_memory")
        episodic_memory = memory_manager.get_memory("episodic_memory")
        semantic_memory = memory_manager.get_memory("semantic_memory")
        graph_memory = memory_manager.get_memory("graph_memory")

        # Add items to each memory system
        working_item = WorkingMemoryItem(content="Test working memory item")
        working_memory.add(working_item)

        episode = Episode(content="Test episodic memory item")
        episodic_memory.add(episode)

        concept = Concept(name="Test", content="Test semantic memory item")
        semantic_memory.add(concept)

        graph_item = GraphMemoryItem(content="Test graph memory item")
        graph_memory.add(graph_item)

        # Convert each memory system to a dictionary
        working_dict = working_memory.to_dict()
        episodic_dict = episodic_memory.to_dict()
        semantic_dict = semantic_memory.to_dict()
        graph_dict = graph_memory.to_dict()

        # Create new memory systems from the dictionaries
        new_working = WorkingMemory.from_dict(working_dict)
        new_episodic = EpisodicMemory.from_dict(episodic_dict)
        new_semantic = SemanticMemory.from_dict(semantic_dict)

        # GraphMemory doesn't have a from_dict method, so we'll skip that

        # Check that the new memory systems have the same items
        assert len(new_working.items) == len(working_memory.items)
        assert len(new_episodic.items) == len(episodic_memory.items)
        assert len(new_semantic.items) == len(semantic_memory.items)

        # Check that the items have the same content
        assert list(new_working.items.values())[0].content == "Test working memory item"
        assert list(new_episodic.items.values())[0].content == "Test episodic memory item"
        assert list(new_semantic.items.values())[0].content == "Test semantic memory item"
