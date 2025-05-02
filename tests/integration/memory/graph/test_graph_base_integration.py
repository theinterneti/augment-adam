"""
Integration tests for augment_adam.memory.graph.base.
"""

import unittest
import pytest
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import tempfile
import os
import json

from augment_adam.memory.core.base import MemoryType
from augment_adam.memory.graph.base import (
    Node, Edge, Relationship, GraphMemoryItem, GraphMemory
)
from augment_adam.memory.graph.networkx import NetworkXMemory
from augment_adam.memory.semantic.base import SemanticMemory, Concept


@pytest.mark.integration
class TestGraphMemoryIntegration(unittest.TestCase):
    """Integration tests for GraphMemory."""

    def setUp(self):
        """Set up the test case."""
        # Create a NetworkXMemory instance
        self.graph_memory = NetworkXMemory(name="test_graph_memory")

        # Create a graph memory item
        self.item = GraphMemoryItem(
            id="graph_item_1",
            content="Test graph memory item",
            metadata={"source": "test", "type": "graph"}
        )

        # Add the item to memory
        self.item_id = self.graph_memory.add(self.item)

        # Create some nodes
        self.node1 = Node(id="node_1", labels=["Person"], properties={"name": "Alice"})
        self.node2 = Node(id="node_2", labels=["Person"], properties={"name": "Bob"})
        self.node3 = Node(id="node_3", labels=["Company"], properties={"name": "Acme Inc."})

        # Create some edges
        self.edge1 = Edge(
            id="edge_1",
            source_id=self.node1.id,
            target_id=self.node2.id,
            relationship=Relationship.RELATED_TO,
            properties={"since": "2025-01-01"}
        )
        self.edge2 = Edge(
            id="edge_2",
            source_id=self.node1.id,
            target_id=self.node3.id,
            relationship=Relationship.MEMBER_OF,
            properties={"role": "Engineer"}
        )

        # Add nodes and edges to the item
        self.graph_memory.add_node(self.item_id, self.node1)
        self.graph_memory.add_node(self.item_id, self.node2)
        self.graph_memory.add_node(self.item_id, self.node3)
        self.graph_memory.add_edge(self.item_id, self.edge1)
        self.graph_memory.add_edge(self.item_id, self.edge2)

    def tearDown(self):
        """Tear down the test case."""
        self.graph_memory = None
        self.item = None

    def test_complex_graph_operations(self):
        """Test complex graph operations and queries."""
        # Create a new item with a more complex graph
        complex_item = GraphMemoryItem(
            id="complex_graph",
            content="Complex graph memory item",
            metadata={"source": "test", "type": "graph", "complexity": "high"}
        )

        # Add the item to memory
        complex_item_id = self.graph_memory.add(complex_item)

        # Create a more complex graph with multiple nodes and relationships
        nodes = []
        for i in range(10):
            node = Node(
                id=f"complex_node_{i}",
                labels=["Node", f"Type{i % 3}"],
                properties={"name": f"Node {i}", "value": i}
            )
            nodes.append(node)
            self.graph_memory.add_node(complex_item_id, node)

        # Create a fully connected graph
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                edge = Edge(
                    id=f"complex_edge_{i}_{j}",
                    source_id=nodes[i].id,
                    target_id=nodes[j].id,
                    relationship=Relationship.RELATED_TO if (i + j) % 2 == 0 else Relationship.SIMILAR_TO,
                    properties={"weight": (i + j) / 20}
                )
                self.graph_memory.add_edge(complex_item_id, edge)

        # Test getting all nodes with a specific label
        type0_nodes = [node for node in complex_item.nodes.values() if "Type0" in node.labels]
        self.assertEqual(len(type0_nodes), 4)  # 0, 3, 6, 9

        # Test getting all edges with a specific relationship
        related_edges = [edge for edge in complex_item.edges.values() if edge.relationship == Relationship.RELATED_TO]
        similar_edges = [edge for edge in complex_item.edges.values() if edge.relationship == Relationship.SIMILAR_TO]

        # There should be 45 total edges in a fully connected graph with 10 nodes
        self.assertEqual(len(complex_item.edges), 45)

        # Test getting neighbors of a specific node
        neighbors = self.graph_memory.get_neighbors(complex_item_id, nodes[0].id)
        self.assertEqual(len(neighbors), 9)  # Connected to all other nodes

        # Test getting edges between specific nodes
        edges_between = self.graph_memory.get_edges_between(complex_item_id, nodes[0].id, nodes[1].id)
        self.assertEqual(len(edges_between), 1)

        # Test search functionality
        # Search for nodes with a specific property value
        search_results = self.graph_memory.search("Node 5", limit=5)
        self.assertIn(complex_item, search_results)

        # Search for nodes with a specific property using a dictionary
        dict_search_results = self.graph_memory.search({"name": "Node 5"}, limit=5)
        self.assertIn(complex_item, dict_search_results)

    def test_serialization_and_persistence(self):
        """Test serialization, deserialization, and persistence of graph memory."""
        # Create a new memory instance with simpler data for serialization
        memory = NetworkXMemory(name="test_serialization_memory")

        # Create a graph memory item
        item = GraphMemoryItem(
            id="serialization_item",
            content="Test serialization item",
            metadata={"source": "test", "type": "graph"}
        )

        # Add the item to memory
        item_id = memory.add(item)

        # Create some nodes
        node1 = Node(id="ser_node_1", labels=["Person"], properties={"name": "Alice"})
        node2 = Node(id="ser_node_2", labels=["Person"], properties={"name": "Bob"})

        # Add nodes to the item
        memory.add_node(item_id, node1)
        memory.add_node(item_id, node2)

        # Create an edge with a proper enum relationship
        edge = Edge(
            id="ser_edge_1",
            source_id=node1.id,
            target_id=node2.id,
            relationship=Relationship.RELATED_TO,  # Use enum instead of string
            properties={"since": "2025-01-01"}
        )

        # Add the edge to the item
        memory.add_edge(item_id, edge)

        # Create a temporary directory for saving the memory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the memory to the temporary directory
            memory.save(temp_dir)

            # Verify the files were created
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "metadata.json")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "items.json")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, f"{item_id}.json")))

            # Load the memory from the temporary directory
            loaded_memory = NetworkXMemory.load(temp_dir)

            # Verify the loaded memory has the same properties
            self.assertEqual(loaded_memory.name, memory.name)
            self.assertEqual(loaded_memory.memory_type, memory.memory_type)

            # Verify the loaded memory has the same items
            self.assertEqual(len(loaded_memory.items), len(memory.items))
            self.assertIn(item_id, loaded_memory.items)

            # Verify the loaded item has the same properties
            loaded_item = loaded_memory.items[item_id]
            self.assertEqual(loaded_item.id, item.id)
            self.assertEqual(loaded_item.content, item.content)
            self.assertEqual(loaded_item.metadata, item.metadata)

            # Verify the loaded item has the same nodes
            self.assertEqual(len(loaded_item.nodes), len(item.nodes))
            for node_id, node in item.nodes.items():
                self.assertIn(node_id, loaded_item.nodes)
                loaded_node = loaded_item.nodes[node_id]
                self.assertEqual(loaded_node.id, node.id)
                self.assertEqual(loaded_node.labels, node.labels)
                self.assertEqual(loaded_node.properties, node.properties)

            # Verify the loaded item has the same edges
            self.assertEqual(len(loaded_item.edges), len(item.edges))
            for edge_id, edge in item.edges.items():
                self.assertIn(edge_id, loaded_item.edges)
                loaded_edge = loaded_item.edges[edge_id]
                self.assertEqual(loaded_edge.id, edge.id)
                self.assertEqual(loaded_edge.source_id, edge.source_id)
                self.assertEqual(loaded_edge.target_id, edge.target_id)
                # Compare relationship - handle both enum and string cases
                if isinstance(edge.relationship, Relationship):
                    # If the original is an enum, the loaded one might be a string with the enum name
                    if isinstance(loaded_edge.relationship, str):
                        self.assertEqual(loaded_edge.relationship, edge.relationship.name)
                    else:
                        # If both are enums, compare them directly
                        self.assertEqual(loaded_edge.relationship, edge.relationship)
                else:
                    # If the original is a string, compare directly
                    self.assertEqual(loaded_edge.relationship, edge.relationship)
                self.assertEqual(loaded_edge.properties, edge.properties)

    def test_integration_with_semantic_memory(self):
        """Test integration of GraphMemory with SemanticMemory."""
        # Create a SemanticMemory instance
        semantic_memory = SemanticMemory(name="test_semantic_memory")

        # Create semantic memory concepts
        semantic_item1 = Concept(
            id="semantic_item_1",
            content="This is a semantic memory item about Alice",
            name="Alice",
            description="A person named Alice",
            metadata={"source": "test", "type": "semantic", "person": "Alice"}
        )

        semantic_item2 = Concept(
            id="semantic_item_2",
            content="This is a semantic memory item about Bob",
            name="Bob",
            description="A person named Bob",
            metadata={"source": "test", "type": "semantic", "person": "Bob"}
        )

        semantic_item3 = Concept(
            id="semantic_item_3",
            content="This is a semantic memory item about Acme Inc.",
            name="Acme Inc.",
            description="A company named Acme Inc.",
            metadata={"source": "test", "type": "semantic", "company": "Acme Inc."}
        )

        # Add the items to semantic memory
        semantic_memory.add(semantic_item1)
        semantic_memory.add(semantic_item2)
        semantic_memory.add(semantic_item3)

        # Create references from graph nodes to semantic items
        self.node1.properties["semantic_ref"] = semantic_item1.id
        self.node2.properties["semantic_ref"] = semantic_item2.id
        self.node3.properties["semantic_ref"] = semantic_item3.id

        # Update the nodes in graph memory
        self.graph_memory.update_node(
            self.item_id,
            self.node1.id,
            properties=self.node1.properties
        )
        self.graph_memory.update_node(
            self.item_id,
            self.node2.id,
            properties=self.node2.properties
        )
        self.graph_memory.update_node(
            self.item_id,
            self.node3.id,
            properties=self.node3.properties
        )

        # Test retrieving semantic information for a graph node
        node1 = self.graph_memory.get_node(self.item_id, self.node1.id)
        semantic_ref1 = node1.properties.get("semantic_ref")
        self.assertIsNotNone(semantic_ref1)

        semantic_item = semantic_memory.get(semantic_ref1)
        self.assertIsNotNone(semantic_item)
        self.assertEqual(semantic_item.content, "This is a semantic memory item about Alice")

        # Test querying graph based on semantic properties
        alice_nodes = [
            node for node in self.item.nodes.values()
            if node.properties.get("semantic_ref") == semantic_item1.id
        ]
        self.assertEqual(len(alice_nodes), 1)
        self.assertEqual(alice_nodes[0].id, self.node1.id)

        # Test combined query across both memory types
        # Find all nodes connected to companies
        company_semantic_items = [
            item for item in semantic_memory.items.values()
            if "company" in item.metadata
        ]
        company_refs = [item.id for item in company_semantic_items]

        company_nodes = [
            node for node in self.item.nodes.values()
            if node.properties.get("semantic_ref") in company_refs
        ]
        self.assertEqual(len(company_nodes), 1)
        self.assertEqual(company_nodes[0].id, self.node3.id)

        # Find all people connected to companies
        company_connections = []
        for edge in self.item.edges.values():
            source_node = self.item.nodes.get(edge.source_id)
            target_node = self.item.nodes.get(edge.target_id)

            if (source_node and target_node and
                "Person" in source_node.labels and
                "Company" in target_node.labels):
                company_connections.append((source_node, target_node, edge))

        self.assertEqual(len(company_connections), 1)
        self.assertEqual(company_connections[0][0].id, self.node1.id)
        self.assertEqual(company_connections[0][1].id, self.node3.id)
        self.assertEqual(company_connections[0][2].relationship, Relationship.MEMBER_OF)


if __name__ == '__main__':
    unittest.main()
