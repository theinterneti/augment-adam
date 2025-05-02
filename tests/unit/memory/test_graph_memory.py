"""
Unit tests for the Graph Memory system.

This module contains tests for the Graph Memory system, including memory
storage, retrieval, and management of graph-based data.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from augment_adam.memory.core.base import MemoryType
from augment_adam.memory.graph.base import GraphMemory, GraphMemoryItem, Node, Edge, Relationship
from augment_adam.memory.graph.networkx import NetworkXMemory


class TestGraphMemory:
    """Tests for the Graph Memory system."""

    @pytest.fixture
    def graph_memory(self):
        """Create a GraphMemory for testing."""
        return GraphMemory(name="test_graph_memory")

    @pytest.fixture
    def sample_node(self):
        """Create a sample Node for testing."""
        return Node(
            labels=["Person"],
            properties={"name": "Alice", "age": 30}
        )

    @pytest.fixture
    def sample_edge(self, sample_nodes):
        """Create a sample Edge for testing."""
        return Edge(
            source_id=sample_nodes["alice"],
            target_id=sample_nodes["bob"],
            relationship=Relationship.RELATED_TO,
            properties={"since": 2020}
        )

    @pytest.fixture
    def sample_nodes(self):
        """Create sample nodes for testing."""
        node1 = Node(labels=["Person"], properties={"name": "Alice", "age": 30})
        node2 = Node(labels=["Person"], properties={"name": "Bob", "age": 25})
        return {"alice": node1.id, "bob": node2.id, "node1": node1, "node2": node2}

    @pytest.fixture
    def sample_graph_item(self, sample_nodes):
        """Create a sample GraphMemoryItem for testing."""
        item = GraphMemoryItem(content="Test graph")

        # Add nodes
        item.add_node(sample_nodes["node1"])
        item.add_node(sample_nodes["node2"])

        # Add edge
        edge = Edge(
            source_id=sample_nodes["alice"],
            target_id=sample_nodes["bob"],
            relationship=Relationship.RELATED_TO,
            properties={"since": 2020}
        )
        item.add_edge(edge)

        return item

    def test_init(self, graph_memory):
        """Test initializing a GraphMemory."""
        assert graph_memory.name == "test_graph_memory"
        assert graph_memory.memory_type == MemoryType.GRAPH
        assert graph_memory.items == {}

    def test_node_init(self, sample_node):
        """Test initializing a Node."""
        assert sample_node.labels == ["Person"]
        assert sample_node.properties == {"name": "Alice", "age": 30}
        assert sample_node.id is not None
        assert sample_node.created_at is not None
        assert sample_node.updated_at is not None
        assert sample_node.embedding is None

    def test_edge_init(self, sample_edge):
        """Test initializing an Edge."""
        assert sample_edge.relationship == Relationship.RELATED_TO
        assert sample_edge.properties == {"since": 2020}
        assert sample_edge.id is not None
        assert sample_edge.created_at is not None
        assert sample_edge.updated_at is not None

    def test_graph_memory_item_init(self):
        """Test initializing a GraphMemoryItem."""
        item = GraphMemoryItem(content="Test graph")
        assert item.content == "Test graph"
        assert item.id is not None
        assert item.created_at is not None
        assert item.updated_at is not None
        assert item.nodes == {}
        assert item.edges == {}

    def test_add_graph_item(self, graph_memory, sample_graph_item):
        """Test adding a graph item to memory."""
        # Add the item
        item_id = graph_memory.add(sample_graph_item)

        # Check that the item was added
        assert item_id == sample_graph_item.id
        assert sample_graph_item.id in graph_memory.items
        assert graph_memory.items[sample_graph_item.id] == sample_graph_item

    def test_get_graph_item(self, graph_memory, sample_graph_item):
        """Test getting a graph item from memory."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Get the item
        retrieved_item = graph_memory.get(sample_graph_item.id)

        # Check that the correct item was retrieved
        assert retrieved_item == sample_graph_item

    def test_get_nonexistent_graph_item(self, graph_memory):
        """Test getting a nonexistent graph item from memory."""
        # Get a nonexistent item
        retrieved_item = graph_memory.get("nonexistent")

        # Check that None was returned
        assert retrieved_item is None

    def test_update_graph_item(self, graph_memory, sample_graph_item):
        """Test updating a graph item in memory."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Update the item
        updated_item = graph_memory.update(
            sample_graph_item.id, content="updated content"
        )

        # Check that the item was updated
        assert updated_item == sample_graph_item
        assert updated_item.content == "updated content"

    def test_update_nonexistent_graph_item(self, graph_memory):
        """Test updating a nonexistent graph item in memory."""
        # Update a nonexistent item
        updated_item = graph_memory.update(
            "nonexistent", content="updated content"
        )

        # Check that None was returned
        assert updated_item is None

    def test_remove_graph_item(self, graph_memory, sample_graph_item):
        """Test removing a graph item from memory."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Remove the item
        result = graph_memory.remove(sample_graph_item.id)

        # Check that the item was removed
        assert result is True
        assert sample_graph_item.id not in graph_memory.items

    def test_remove_nonexistent_graph_item(self, graph_memory):
        """Test removing a nonexistent graph item from memory."""
        # Remove a nonexistent item
        result = graph_memory.remove("nonexistent")

        # Check that False was returned
        assert result is False

    def test_clear_graph_items(self, graph_memory, sample_graph_item):
        """Test clearing all graph items from memory."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Clear the memory
        graph_memory.clear()

        # Check that the memory is empty
        assert len(graph_memory.items) == 0

    def test_add_node(self, graph_memory, sample_graph_item, sample_node):
        """Test adding a node to a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Add a new node
        new_node = Node(labels=["Location"], properties={"name": "New York"})
        node_id = graph_memory.add_node(sample_graph_item.id, new_node)

        # Check that the node was added
        assert node_id == new_node.id
        assert new_node.id in sample_graph_item.nodes
        assert sample_graph_item.nodes[new_node.id] == new_node

    def test_add_node_to_nonexistent_item(self, graph_memory, sample_node):
        """Test adding a node to a nonexistent graph item."""
        # Add a node to a nonexistent item
        node_id = graph_memory.add_node("nonexistent", sample_node)

        # Check that None was returned
        assert node_id is None

    def test_get_node(self, graph_memory, sample_graph_item, sample_nodes):
        """Test getting a node from a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Get the node
        retrieved_node = graph_memory.get_node(sample_graph_item.id, sample_nodes["alice"])

        # Check that the correct node was retrieved
        assert retrieved_node.id == sample_nodes["alice"]
        assert retrieved_node.properties["name"] == "Alice"

    def test_get_nonexistent_node(self, graph_memory, sample_graph_item):
        """Test getting a nonexistent node from a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Get a nonexistent node
        retrieved_node = graph_memory.get_node(sample_graph_item.id, "nonexistent")

        # Check that None was returned
        assert retrieved_node is None

    def test_get_node_from_nonexistent_item(self, graph_memory):
        """Test getting a node from a nonexistent graph item."""
        # Get a node from a nonexistent item
        retrieved_node = graph_memory.get_node("nonexistent", "nonexistent")

        # Check that None was returned
        assert retrieved_node is None

    def test_update_node(self, graph_memory, sample_graph_item, sample_nodes):
        """Test updating a node in a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Update the node
        updated_node = graph_memory.update_node(
            sample_graph_item.id,
            sample_nodes["alice"],
            labels=["Person", "Employee"],
            properties={"name": "Alice", "age": 31, "job": "Engineer"}
        )

        # Check that the node was updated
        assert updated_node.id == sample_nodes["alice"]
        assert updated_node.labels == ["Person", "Employee"]
        assert updated_node.properties == {"name": "Alice", "age": 31, "job": "Engineer"}

    def test_update_nonexistent_node(self, graph_memory, sample_graph_item):
        """Test updating a nonexistent node in a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Update a nonexistent node
        updated_node = graph_memory.update_node(
            sample_graph_item.id,
            "nonexistent",
            labels=["Person"],
            properties={"name": "Charlie"}
        )

        # Check that None was returned
        assert updated_node is None

    def test_update_node_in_nonexistent_item(self, graph_memory):
        """Test updating a node in a nonexistent graph item."""
        # Update a node in a nonexistent item
        updated_node = graph_memory.update_node(
            "nonexistent",
            "nonexistent",
            labels=["Person"],
            properties={"name": "Charlie"}
        )

        # Check that None was returned
        assert updated_node is None

    def test_remove_node(self, graph_memory, sample_graph_item, sample_nodes):
        """Test removing a node from a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Remove the node
        result = graph_memory.remove_node(sample_graph_item.id, sample_nodes["alice"])

        # Check that the node was removed
        assert result is True
        assert sample_nodes["alice"] not in sample_graph_item.nodes

    def test_remove_nonexistent_node(self, graph_memory, sample_graph_item):
        """Test removing a nonexistent node from a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Remove a nonexistent node
        result = graph_memory.remove_node(sample_graph_item.id, "nonexistent")

        # Check that False was returned
        assert result is False

    def test_remove_node_from_nonexistent_item(self, graph_memory):
        """Test removing a node from a nonexistent graph item."""
        # Remove a node from a nonexistent item
        result = graph_memory.remove_node("nonexistent", "nonexistent")

        # Check that False was returned
        assert result is False

    def test_add_edge(self, graph_memory, sample_graph_item, sample_nodes):
        """Test adding an edge to a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Add a new edge
        new_edge = Edge(
            source_id=sample_nodes["bob"],
            target_id=sample_nodes["alice"],
            relationship=Relationship.RELATED_TO,
            properties={"since": 2020}
        )
        edge_id = graph_memory.add_edge(sample_graph_item.id, new_edge)

        # Check that the edge was added
        assert edge_id == new_edge.id
        assert new_edge.id in sample_graph_item.edges
        assert sample_graph_item.edges[new_edge.id] == new_edge

    def test_add_edge_to_nonexistent_item(self, graph_memory, sample_edge):
        """Test adding an edge to a nonexistent graph item."""
        # Add an edge to a nonexistent item
        edge_id = graph_memory.add_edge("nonexistent", sample_edge)

        # Check that None was returned
        assert edge_id is None

    def test_get_edge(self, graph_memory, sample_graph_item):
        """Test getting an edge from a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Get the first edge
        edge_id = next(iter(sample_graph_item.edges))
        retrieved_edge = graph_memory.get_edge(sample_graph_item.id, edge_id)

        # Check that the correct edge was retrieved
        assert retrieved_edge.id == edge_id
        assert retrieved_edge.relationship == Relationship.RELATED_TO
        assert retrieved_edge.properties["since"] == 2020

    def test_get_nonexistent_edge(self, graph_memory, sample_graph_item):
        """Test getting a nonexistent edge from a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Get a nonexistent edge
        retrieved_edge = graph_memory.get_edge(sample_graph_item.id, "nonexistent")

        # Check that None was returned
        assert retrieved_edge is None

    def test_get_edge_from_nonexistent_item(self, graph_memory):
        """Test getting an edge from a nonexistent graph item."""
        # Get an edge from a nonexistent item
        retrieved_edge = graph_memory.get_edge("nonexistent", "nonexistent")

        # Check that None was returned
        assert retrieved_edge is None

    def test_update_edge(self, graph_memory, sample_graph_item):
        """Test updating an edge in a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Get the first edge
        edge_id = next(iter(sample_graph_item.edges))

        # Update the edge
        updated_edge = graph_memory.update_edge(
            sample_graph_item.id,
            edge_id,
            relationship=Relationship.RELATED_TO,
            properties={"since": 2021, "close": True}
        )

        # Check that the edge was updated
        assert updated_edge.id == edge_id
        assert updated_edge.relationship == Relationship.RELATED_TO
        assert updated_edge.properties["since"] == 2021
        assert updated_edge.properties["close"] is True

    def test_update_nonexistent_edge(self, graph_memory, sample_graph_item):
        """Test updating a nonexistent edge in a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Update a nonexistent edge
        updated_edge = graph_memory.update_edge(
            sample_graph_item.id,
            "nonexistent",
            relationship=Relationship.RELATED_TO,
            properties={"since": 2021}
        )

        # Check that None was returned
        assert updated_edge is None

    def test_update_edge_in_nonexistent_item(self, graph_memory):
        """Test updating an edge in a nonexistent graph item."""
        # Update an edge in a nonexistent item
        updated_edge = graph_memory.update_edge(
            "nonexistent",
            "nonexistent",
            relationship=Relationship.RELATED_TO,
            properties={"since": 2021}
        )

        # Check that None was returned
        assert updated_edge is None

    def test_remove_edge(self, graph_memory, sample_graph_item):
        """Test removing an edge from a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Get the first edge
        edge_id = next(iter(sample_graph_item.edges))

        # Remove the edge
        result = graph_memory.remove_edge(sample_graph_item.id, edge_id)

        # Check that the edge was removed
        assert result is True
        assert edge_id not in sample_graph_item.edges

    def test_remove_nonexistent_edge(self, graph_memory, sample_graph_item):
        """Test removing a nonexistent edge from a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Remove a nonexistent edge
        result = graph_memory.remove_edge(sample_graph_item.id, "nonexistent")

        # Check that False was returned
        assert result is False

    def test_remove_edge_from_nonexistent_item(self, graph_memory):
        """Test removing an edge from a nonexistent graph item."""
        # Remove an edge from a nonexistent item
        result = graph_memory.remove_edge("nonexistent", "nonexistent")

        # Check that False was returned
        assert result is False

    def test_get_neighbors(self, graph_memory, sample_graph_item, sample_nodes):
        """Test getting neighbors of a node in a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Get neighbors of Alice
        neighbors = graph_memory.get_neighbors(sample_graph_item.id, sample_nodes["alice"])

        # Check that Bob is a neighbor of Alice
        assert len(neighbors) == 1
        assert neighbors[0].id == sample_nodes["bob"]
        assert neighbors[0].properties["name"] == "Bob"

    def test_get_neighbors_of_nonexistent_node(self, graph_memory, sample_graph_item):
        """Test getting neighbors of a nonexistent node in a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Get neighbors of a nonexistent node
        neighbors = graph_memory.get_neighbors(sample_graph_item.id, "nonexistent")

        # Check that an empty list was returned
        assert neighbors == []

    def test_get_neighbors_from_nonexistent_item(self, graph_memory):
        """Test getting neighbors from a nonexistent graph item."""
        # Get neighbors from a nonexistent item
        neighbors = graph_memory.get_neighbors("nonexistent", "nonexistent")

        # Check that an empty list was returned
        assert neighbors == []

    def test_get_edges_between(self, graph_memory, sample_graph_item, sample_nodes):
        """Test getting edges between two nodes in a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Get edges between Alice and Bob
        edges = graph_memory.get_edges_between(
            sample_graph_item.id,
            sample_nodes["alice"],
            sample_nodes["bob"]
        )

        # Check that there is one edge between Alice and Bob
        assert len(edges) == 1
        assert edges[0].source_id == sample_nodes["alice"]
        assert edges[0].target_id == sample_nodes["bob"]
        assert edges[0].relationship == Relationship.RELATED_TO

    def test_get_edges_between_nonexistent_nodes(self, graph_memory, sample_graph_item, sample_nodes):
        """Test getting edges between nonexistent nodes in a graph item."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Get edges between Alice and a nonexistent node
        edges = graph_memory.get_edges_between(
            sample_graph_item.id,
            sample_nodes["alice"],
            "nonexistent"
        )

        # Check that an empty list was returned
        assert edges == []

    def test_get_edges_between_from_nonexistent_item(self, graph_memory):
        """Test getting edges between from a nonexistent graph item."""
        # Get edges between from a nonexistent item
        edges = graph_memory.get_edges_between("nonexistent", "node1", "node2")

        # Check that an empty list was returned
        assert edges == []

    def test_node_to_dict(self, sample_node):
        """Test converting a node to a dictionary."""
        # Convert the node to a dictionary
        node_dict = sample_node.to_dict()

        # Check the dictionary
        assert node_dict["id"] == sample_node.id
        assert node_dict["labels"] == ["Person"]
        assert node_dict["properties"] == {"name": "Alice", "age": 30}
        assert "created_at" in node_dict
        assert "updated_at" in node_dict

    def test_node_from_dict(self):
        """Test creating a node from a dictionary."""
        # Create a dictionary
        node_dict = {
            "id": "test_id",
            "labels": ["Person", "Employee"],
            "properties": {"name": "Alice", "age": 30, "job": "Engineer"},
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }

        # Create a node from the dictionary
        node = Node.from_dict(node_dict)

        # Check the node
        assert node.id == "test_id"
        assert node.labels == ["Person", "Employee"]
        assert node.properties == {"name": "Alice", "age": 30, "job": "Engineer"}
        assert node.created_at == "2023-01-01T00:00:00"
        assert node.updated_at == "2023-01-01T00:00:00"

    def test_edge_to_dict(self, sample_edge):
        """Test converting an edge to a dictionary."""
        # Convert the edge to a dictionary
        edge_dict = sample_edge.to_dict()

        # Check the dictionary
        assert edge_dict["id"] == sample_edge.id
        assert edge_dict["source_id"] == sample_edge.source_id
        assert edge_dict["target_id"] == sample_edge.target_id
        assert edge_dict["relationship"] == "RELATED_TO"
        assert edge_dict["properties"] == {"since": 2020}
        assert "created_at" in edge_dict
        assert "updated_at" in edge_dict

    def test_edge_from_dict(self):
        """Test creating an edge from a dictionary."""
        # Create a dictionary
        edge_dict = {
            "id": "test_id",
            "source_id": "source_id",
            "target_id": "target_id",
            "relationship": "RELATED_TO",
            "properties": {"since": 2020},
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }

        # Create an edge from the dictionary
        edge = Edge.from_dict(edge_dict)

        # Check the edge
        assert edge.id == "test_id"
        assert edge.source_id == "source_id"
        assert edge.target_id == "target_id"
        assert edge.relationship == Relationship.RELATED_TO
        assert edge.properties == {"since": 2020}
        assert edge.created_at == "2023-01-01T00:00:00"
        assert edge.updated_at == "2023-01-01T00:00:00"

    def test_graph_memory_item_to_dict(self, sample_graph_item):
        """Test converting a graph memory item to a dictionary."""
        # Convert the item to a dictionary
        item_dict = sample_graph_item.to_dict()

        # Check the dictionary
        assert item_dict["id"] == sample_graph_item.id
        assert item_dict["content"] == "Test graph"
        assert "created_at" in item_dict
        assert "updated_at" in item_dict
        assert "nodes" in item_dict
        assert "edges" in item_dict
        assert len(item_dict["nodes"]) == 2
        assert len(item_dict["edges"]) == 1

    def test_graph_memory_item_from_dict(self):
        """Test creating a graph memory item from a dictionary."""
        # Create a dictionary
        item_dict = {
            "id": "test_id",
            "content": "Test graph",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "nodes": {
                "node1": {
                    "id": "node1",
                    "labels": ["Person"],
                    "properties": {"name": "Alice", "age": 30},
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00"
                },
                "node2": {
                    "id": "node2",
                    "labels": ["Person"],
                    "properties": {"name": "Bob", "age": 25},
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00"
                }
            },
            "edges": {
                "edge1": {
                    "id": "edge1",
                    "source_id": "node1",
                    "target_id": "node2",
                    "relationship": "RELATED_TO",
                    "properties": {"since": 2020},
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00"
                }
            }
        }

        # Create an item from the dictionary
        item = GraphMemoryItem.from_dict(item_dict)

        # Check the item
        assert item.id == "test_id"
        assert item.content == "Test graph"
        assert item.created_at == "2023-01-01T00:00:00"
        assert item.updated_at == "2023-01-01T00:00:00"
        assert len(item.nodes) == 2
        assert "node1" in item.nodes
        assert "node2" in item.nodes
        assert len(item.edges) == 1
        assert "edge1" in item.edges
        assert item.edges["edge1"].source_id == "node1"
        assert item.edges["edge1"].target_id == "node2"
        assert item.edges["edge1"].relationship == Relationship.RELATED_TO

    def test_graph_memory_to_dict(self, graph_memory, sample_graph_item):
        """Test converting a graph memory to a dictionary."""
        # Add the item
        graph_memory.add(sample_graph_item)

        # Convert the memory to a dictionary
        memory_dict = graph_memory.to_dict()

        # Check the dictionary
        assert memory_dict["name"] == "test_graph_memory"
        assert memory_dict["memory_type"] == "GRAPH"
        assert "items" in memory_dict
        assert sample_graph_item.id in memory_dict["items"]

    def test_graph_memory_item_from_dict_to_dict(self):
        """Test converting a graph memory item to and from a dictionary."""
        # Create a dictionary
        item_dict = {
            "id": "item1",
            "content": "Test graph",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "nodes": {
                "node1": {
                    "id": "node1",
                    "labels": ["Person"],
                    "properties": {"name": "Alice"},
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00"
                }
            },
            "edges": {}
        }

        # Create an item from the dictionary
        item = GraphMemoryItem.from_dict(item_dict)

        # Check the item
        assert item.id == "item1"
        assert item.content == "Test graph"
        assert item.created_at == "2023-01-01T00:00:00"
        assert item.updated_at == "2023-01-01T00:00:00"
        assert len(item.nodes) == 1
        assert "node1" in item.nodes
        assert item.nodes["node1"].labels == ["Person"]
        assert item.nodes["node1"].properties == {"name": "Alice"}

        # Convert back to dictionary
        item_dict2 = item.to_dict()

        # Check the dictionary
        assert item_dict2["id"] == "item1"
        assert item_dict2["content"] == "Test graph"
        assert item_dict2["created_at"] == "2023-01-01T00:00:00"
        assert item_dict2["updated_at"] == "2023-01-01T00:00:00"
        assert len(item_dict2["nodes"]) == 1
        assert "node1" in item_dict2["nodes"]
