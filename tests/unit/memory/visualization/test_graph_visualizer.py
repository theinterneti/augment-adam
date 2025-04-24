"""
Tests for the graph visualizer.
"""

import os
import pytest
import asyncio
from unittest.mock import MagicMock, patch

from augment_adam.memory.visualization.graph_visualizer import (
    MemoryGraphVisualizer,
    visualize_memory_graph,
    save_memory_graph_visualization
)


class TestMemoryGraphVisualizer:
    """Tests for the MemoryGraphVisualizer class."""
    
    @pytest.fixture
    def mock_neo4j_client(self):
        """Mock Neo4j client for testing."""
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        
        # Mock the driver.session() context manager
        mock_client.driver.session.return_value.__aenter__.return_value = mock_session
        mock_session.run.return_value = mock_result
        
        # Mock the result.values() method
        mock_result.values.return_value = []
        
        return mock_client
    
    @pytest.fixture
    def visualizer(self, mock_neo4j_client):
        """MemoryGraphVisualizer instance for testing."""
        return MemoryGraphVisualizer(client=mock_neo4j_client)
    
    @pytest.mark.asyncio
    async def test_get_graph_data_empty(self, visualizer):
        """Test getting graph data when the graph is empty."""
        nodes, edges = await visualizer.get_graph_data()
        
        assert nodes == []
        assert edges == []
        
        # Verify that the client was called correctly
        visualizer.client.driver.session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_graph_data_with_center_node(self, visualizer, mock_neo4j_client):
        """Test getting graph data with a center node."""
        # Mock the result.values() method to return a path with nodes and relationships
        mock_path = MagicMock()
        
        # Create mock nodes
        mock_node1 = MagicMock()
        mock_node1.id = 1
        mock_node1.labels = ["Vector"]
        mock_node1.__getitem__.side_effect = lambda key: {"id": "node1", "metadata": '{"text": "Node 1"}'}[key]
        mock_node1.items.return_value = [("id", "node1"), ("metadata", '{"text": "Node 1"}')]
        
        mock_node2 = MagicMock()
        mock_node2.id = 2
        mock_node2.labels = ["Vector"]
        mock_node2.__getitem__.side_effect = lambda key: {"id": "node2", "metadata": '{"text": "Node 2"}'}[key]
        mock_node2.items.return_value = [("id", "node2"), ("metadata", '{"text": "Node 2"}')]
        
        # Create mock relationship
        mock_rel = MagicMock()
        mock_rel.id = 1
        mock_rel.type = "RELATED_TO"
        mock_rel.start_node = mock_node1
        mock_rel.end_node = mock_node2
        mock_rel.items.return_value = []
        
        # Set up the path
        mock_path.nodes = [mock_node1, mock_node2]
        mock_path.relationships = [mock_rel]
        
        # Mock the result.values() method
        mock_neo4j_client.driver.session.return_value.__aenter__.return_value.run.return_value.values.return_value = [[mock_path]]
        
        # Call the method
        nodes, edges = await visualizer.get_graph_data(center_node_id="node1")
        
        # Verify the results
        assert len(nodes) == 2
        assert nodes[0]["id"] == "node1"
        assert nodes[1]["id"] == "node2"
        
        assert len(edges) == 1
        assert edges[0]["from"] == "node1"
        assert edges[0]["to"] == "node2"
        assert edges[0]["label"] == "RELATED_TO"
    
    @pytest.mark.asyncio
    async def test_generate_visualization(self, visualizer):
        """Test generating a visualization."""
        # Mock the get_graph_data method
        visualizer.get_graph_data = MagicMock(return_value=asyncio.Future())
        visualizer.get_graph_data.return_value.set_result((
            [
                {"id": "node1", "label": "Node 1", "metadata": {"text": "Node 1"}},
                {"id": "node2", "label": "Node 2", "metadata": {"text": "Node 2"}}
            ],
            [
                {"id": "rel1", "from": "node1", "to": "node2", "label": "RELATED_TO"}
            ]
        ))
        
        # Call the method
        html = await visualizer.generate_visualization()
        
        # Verify the results
        assert "<!DOCTYPE html>" in html
        assert "<title>Memory Graph Visualization</title>" in html
        assert "const nodes = " in html
        assert "const edges = " in html
    
    @pytest.mark.asyncio
    async def test_save_visualization(self, visualizer, tmp_path):
        """Test saving a visualization to a file."""
        # Mock the generate_visualization method
        visualizer.generate_visualization = MagicMock(return_value=asyncio.Future())
        visualizer.generate_visualization.return_value.set_result("<html>Test</html>")
        
        # Call the method
        output_path = str(tmp_path / "graph.html")
        result = await visualizer.save_visualization(output_path)
        
        # Verify the results
        assert result == output_path
        assert os.path.exists(output_path)
        
        with open(output_path, "r") as f:
            content = f.read()
            assert content == "<html>Test</html>"


@patch("augment_adam.memory.visualization.graph_visualizer.MemoryGraphVisualizer")
def test_visualize_memory_graph(mock_visualizer_class):
    """Test the visualize_memory_graph function."""
    # Mock the MemoryGraphVisualizer.generate_visualization method
    mock_visualizer = MagicMock()
    mock_visualizer_class.return_value = mock_visualizer
    
    # Mock the asyncio.run function
    mock_future = MagicMock()
    mock_future.return_value = "<html>Test</html>"
    mock_visualizer.generate_visualization.return_value = mock_future
    
    # Call the function
    with patch("asyncio.run", return_value="<html>Test</html>"):
        result = visualize_memory_graph(center_node_id="node1")
    
    # Verify the results
    assert result == "<html>Test</html>"
    mock_visualizer_class.assert_called_once()
    mock_visualizer.generate_visualization.assert_called_once_with(
        center_node_id="node1",
        collection_name="default",
        depth=2,
        limit=100
    )


@patch("augment_adam.memory.visualization.graph_visualizer.MemoryGraphVisualizer")
def test_save_memory_graph_visualization(mock_visualizer_class, tmp_path):
    """Test the save_memory_graph_visualization function."""
    # Mock the MemoryGraphVisualizer.save_visualization method
    mock_visualizer = MagicMock()
    mock_visualizer_class.return_value = mock_visualizer
    
    # Mock the asyncio.run function
    output_path = str(tmp_path / "graph.html")
    mock_future = MagicMock()
    mock_future.return_value = output_path
    mock_visualizer.save_visualization.return_value = mock_future
    
    # Call the function
    with patch("asyncio.run", return_value=output_path):
        result = save_memory_graph_visualization(output_path, center_node_id="node1")
    
    # Verify the results
    assert result == output_path
    mock_visualizer_class.assert_called_once()
    mock_visualizer.save_visualization.assert_called_once_with(
        output_path=output_path,
        center_node_id="node1",
        collection_name="default",
        depth=2,
        limit=100
    )
