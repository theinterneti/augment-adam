"""
Tests for the Jinja2 utilities.
"""

import os
import pytest
from pathlib import Path

from augment_adam.utils.jinja_utils import (
    JinjaRenderer,
    render_template,
    render_cypher_query,
    render_graph_visualization,
    render_test_template,
    render_docstring
)


class TestJinjaRenderer:
    """Tests for the JinjaRenderer class."""
    
    def test_init_with_default_templates_dir(self):
        """Test initializing with the default templates directory."""
        renderer = JinjaRenderer()
        assert renderer.env is not None
    
    def test_init_with_custom_templates_dir(self, tmp_path):
        """Test initializing with a custom templates directory."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        
        # Create a test template
        test_template = templates_dir / "test.j2"
        test_template.write_text("Hello, {{ name }}!")
        
        renderer = JinjaRenderer(str(templates_dir))
        assert renderer.env is not None
        
        # Test rendering the template
        result = renderer.render_template("test.j2", {"name": "World"})
        assert result == "Hello, World!"


class TestRenderCypherQuery:
    """Tests for the render_cypher_query function."""
    
    def test_render_create_node_query(self):
        """Test rendering a create node query."""
        query = render_cypher_query(
            query_type="create_node",
            node_label="Vector",
            collection_name="test_collection",
            return_node=False
        )
        
        assert "MERGE (n:Vector :test_collection {id: $id})" in query
        assert "SET n.embedding = $embedding" in query
        assert "SET n.metadata = $metadata" in query
        assert "SET n.timestamp = timestamp()" in query
    
    def test_render_search_vector_query(self):
        """Test rendering a search vector query."""
        query = render_cypher_query(
            query_type="search_vector",
            index_name="vector_index_test",
            filter_conditions="json.type = 'memory'"
        )
        
        assert "CALL db.index.vector.queryNodes('vector_index_test', $k, $embedding)" in query
        assert "WITH node, score, apoc.convert.fromJsonMap(node.metadata) AS json" in query
        assert "WHERE json.type = 'memory'" in query
        assert "RETURN node.id AS id, score, node.metadata AS metadata" in query
        assert "ORDER BY score DESC" in query
        assert "LIMIT $k" in query
    
    def test_render_get_by_id_query(self):
        """Test rendering a get by ID query."""
        query = render_cypher_query(
            query_type="get_by_id",
            node_label="Vector",
            collection_name="test_collection"
        )
        
        assert "MATCH (n:Vector :test_collection {id: $id})" in query
        assert "RETURN n.metadata AS metadata" in query
    
    def test_render_delete_node_query(self):
        """Test rendering a delete node query."""
        query = render_cypher_query(
            query_type="delete_node",
            node_label="Vector",
            collection_name="test_collection",
            delete_relationships=True
        )
        
        assert "MATCH (n:Vector :test_collection {id: $id})" in query
        assert "DETACH DELETE n" in query
        assert "RETURN count(n) as deleted_count" in query
    
    def test_render_clear_collection_query(self):
        """Test rendering a clear collection query."""
        query = render_cypher_query(
            query_type="clear_collection",
            node_label="Vector",
            collection_name="test_collection",
            delete_relationships=False
        )
        
        assert "MATCH (n:Vector :test_collection)" in query
        assert "DELETE n" in query
        assert "RETURN count(n) as deleted_count" in query
    
    def test_render_create_index_query(self):
        """Test rendering a create index query."""
        query = render_cypher_query(
            query_type="create_index",
            index_name="vector_index_test",
            node_label="Vector",
            collection_name="test_collection",
            vector_dimensions=384,
            similarity_function="cosine"
        )
        
        assert "CREATE VECTOR INDEX vector_index_test IF NOT EXISTS" in query
        assert "FOR (n:Vector :test_collection) ON (n.embedding)" in query
        assert "`vector.dimensions`: 384" in query
        assert "`vector.similarity_function`: 'cosine'" in query
    
    def test_render_create_relationship_query(self):
        """Test rendering a create relationship query."""
        query = render_cypher_query(
            query_type="create_relationship",
            from_label="Vector",
            to_label="Vector",
            relationship_type="RELATED_TO",
            collection_name="test_collection",
            properties=True,
            return_relationship=False
        )
        
        assert "MATCH (from:Vector :test_collection {id: $from_id})" in query
        assert "MATCH (to:Vector :test_collection {id: $to_id})" in query
        assert "MERGE (from)-[r:RELATED_TO]->(to)" in query
        assert "SET r += $properties" in query


class TestRenderGraphVisualization:
    """Tests for the render_graph_visualization function."""
    
    def test_render_graph_visualization(self):
        """Test rendering a graph visualization."""
        nodes = [
            {"id": "1", "label": "Node 1", "metadata": {"text": "Test node 1"}},
            {"id": "2", "label": "Node 2", "metadata": {"text": "Test node 2"}}
        ]
        
        edges = [
            {"id": "1", "from": "1", "to": "2", "label": "RELATED_TO"}
        ]
        
        node_types = [
            {"label": "Vector", "color": "#97C2FC"},
            {"label": "Memory", "color": "#FB7E81"}
        ]
        
        html = render_graph_visualization(nodes, edges, node_types)
        
        assert "<!DOCTYPE html>" in html
        assert "<title>Memory Graph Visualization</title>" in html
        assert "const nodes = " in html
        assert "const edges = " in html
        assert "Vector" in html
        assert "Memory" in html


class TestRenderTestTemplate:
    """Tests for the render_test_template function."""
    
    def test_render_test_template(self):
        """Test rendering a test template."""
        imports = [
            "import pytest",
            "from augment_adam.utils.jinja_utils import JinjaRenderer"
        ]
        
        tests = [
            {
                "name": "test_render_template",
                "description": "Test rendering a template.",
                "fixtures": ["renderer"],
                "arrange": "template = 'Hello, {{ name }}!'",
                "act": "result = renderer.render_template('test.j2', {'name': 'World'})",
                "assert": "assert result == 'Hello, World!'"
            }
        ]
        
        class_under_test = {
            "name": "JinjaRenderer",
            "methods": ["render_template", "render_cypher_query"]
        }
        
        fixtures = [
            {
                "name": "renderer",
                "description": "JinjaRenderer instance for testing.",
                "code": "return JinjaRenderer()"
            }
        ]
        
        test_code = render_test_template(imports, tests, class_under_test, fixtures)
        
        assert "import pytest" in test_code
        assert "from augment_adam.utils.jinja_utils import JinjaRenderer" in test_code
        assert "class TestJinjaRenderer:" in test_code
        assert "@pytest.fixture" in test_code
        assert "def renderer(self):" in test_code
        assert "def test_render_template(self, renderer):" in test_code
        assert "# Arrange" in test_code
        assert "# Act" in test_code
        assert "# Assert" in test_code


class TestRenderDocstring:
    """Tests for the render_docstring function."""
    
    def test_render_function_docstring(self):
        """Test rendering a function docstring."""
        docstring = render_docstring(
            docstring_type="function",
            summary="Render a template with the given context.",
            description="This function renders a Jinja2 template with the provided context.",
            parameters=[
                {"name": "template_name", "type": "str", "description": "Name of the template to render."},
                {"name": "context", "type": "Dict[str, Any]", "description": "Context to use for rendering the template."}
            ],
            returns={
                "type": "str",
                "description": "Rendered template."
            },
            examples=[
                ">>> render_template('hello.j2', {'name': 'World'})",
                "Hello, World!"
            ]
        )
        
        assert "Render a template with the given context." in docstring
        assert "This function renders a Jinja2 template with the provided context." in docstring
        assert "Parameters" in docstring
        assert "template_name : str" in docstring
        assert "context : Dict[str, Any]" in docstring
        assert "Returns" in docstring
        assert "str" in docstring
        assert "Rendered template." in docstring
        assert "Examples" in docstring
        assert ">>> render_template('hello.j2', {'name': 'World'})" in docstring
        assert "Hello, World!" in docstring
    
    def test_render_class_docstring(self):
        """Test rendering a class docstring."""
        docstring = render_docstring(
            docstring_type="class",
            summary="Utility class for rendering Jinja2 templates.",
            description="This class provides methods for rendering Jinja2 templates.",
            attributes=[
                {"name": "env", "type": "Environment", "description": "Jinja2 environment."},
                {"name": "templates_dir", "type": "str", "description": "Directory containing the templates."}
            ],
            examples=[
                ">>> renderer = JinjaRenderer()",
                ">>> renderer.render_template('hello.j2', {'name': 'World'})",
                "Hello, World!"
            ]
        )
        
        assert "Utility class for rendering Jinja2 templates." in docstring
        assert "This class provides methods for rendering Jinja2 templates." in docstring
        assert "Attributes" in docstring
        assert "env : Environment" in docstring
        assert "templates_dir : str" in docstring
        assert "Examples" in docstring
        assert ">>> renderer = JinjaRenderer()" in docstring
        assert ">>> renderer.render_template('hello.j2', {'name': 'World'})" in docstring
        assert "Hello, World!" in docstring
    
    def test_render_module_docstring(self):
        """Test rendering a module docstring."""
        docstring = render_docstring(
            docstring_type="module",
            summary="Jinja2 utilities for rendering templates.",
            description="This module provides utilities for rendering Jinja2 templates.",
            examples=[
                ">>> from augment_adam.utils.jinja_utils import render_template",
                ">>> render_template('hello.j2', {'name': 'World'})",
                "Hello, World!"
            ],
            notes="This module requires Jinja2 to be installed."
        )
        
        assert "Jinja2 utilities for rendering templates." in docstring
        assert "This module provides utilities for rendering Jinja2 templates." in docstring
        assert "Examples" in docstring
        assert ">>> from augment_adam.utils.jinja_utils import render_template" in docstring
        assert ">>> render_template('hello.j2', {'name': 'World'})" in docstring
        assert "Hello, World!" in docstring
        assert "Notes" in docstring
        assert "This module requires Jinja2 to be installed." in docstring
