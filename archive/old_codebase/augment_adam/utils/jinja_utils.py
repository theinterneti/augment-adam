"""
Jinja2 utilities for rendering templates.
"""

import os
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

class JinjaRenderer:
    """
    Utility class for rendering Jinja2 templates.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the Jinja2 renderer.
        
        Parameters
        ----------
        templates_dir : str, optional
            Directory containing the templates. If None, uses the default templates directory.
        """
        if templates_dir is None:
            # Use the default templates directory
            package_dir = Path(__file__).parent.parent.parent
            templates_dir = os.path.join(package_dir, "templates")
        
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['tojson'] = lambda obj: json.dumps(obj)
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Parameters
        ----------
        template_name : str
            Name of the template to render.
        context : Dict[str, Any]
            Context to use for rendering the template.
        
        Returns
        -------
        str
            Rendered template.
        """
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def render_cypher_query(self, query_type: str, **kwargs) -> str:
        """
        Render a Cypher query template.
        
        Parameters
        ----------
        query_type : str
            Type of query to render (e.g., "create_node", "search_vector").
        **kwargs : Dict[str, Any]
            Additional context for rendering the template.
        
        Returns
        -------
        str
            Rendered Cypher query.
        """
        context = {"query_type": query_type, **kwargs}
        return self.render_template("memory/cypher_query.j2", context)
    
    def render_graph_visualization(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], 
                                  node_types: List[Dict[str, Any]]) -> str:
        """
        Render a graph visualization template.
        
        Parameters
        ----------
        nodes : List[Dict[str, Any]]
            List of nodes to visualize.
        edges : List[Dict[str, Any]]
            List of edges to visualize.
        node_types : List[Dict[str, Any]]
            List of node types for the legend.
        
        Returns
        -------
        str
            Rendered HTML for graph visualization.
        """
        context = {
            "nodes": nodes,
            "edges": edges,
            "node_types": node_types
        }
        return self.render_template("memory/graph_visualization.j2", context)
    
    def render_test_template(self, imports: List[str], tests: List[Dict[str, Any]], 
                           class_under_test: Optional[Dict[str, Any]] = None,
                           fixtures: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Render a test template.
        
        Parameters
        ----------
        imports : List[str]
            List of import statements.
        tests : List[Dict[str, Any]]
            List of test definitions.
        class_under_test : Dict[str, Any], optional
            Information about the class under test.
        fixtures : List[Dict[str, Any]], optional
            List of test fixtures.
        
        Returns
        -------
        str
            Rendered test file.
        """
        context = {
            "imports": imports,
            "tests": tests,
            "class_under_test": class_under_test,
            "fixtures": fixtures or []
        }
        return self.render_template("test_template.j2", context)
    
    def render_docstring(self, docstring_type: str, summary: str, **kwargs) -> str:
        """
        Render a docstring template.
        
        Parameters
        ----------
        docstring_type : str
            Type of docstring to render (e.g., "function", "class", "module").
        summary : str
            Summary of the docstring.
        **kwargs : Dict[str, Any]
            Additional context for rendering the template.
        
        Returns
        -------
        str
            Rendered docstring.
        """
        context = {
            "docstring_type": docstring_type,
            "summary": summary,
            **kwargs
        }
        return self.render_template("docstring_template.j2", context)

def render_template(template_name: str, context: Dict[str, Any]) -> str:
    """
    Render a template with the given context.
    
    Parameters
    ----------
    template_name : str
        Name of the template to render.
    context : Dict[str, Any]
        Context to use for rendering the template.
    
    Returns
    -------
    str
        Rendered template.
    """
    renderer = JinjaRenderer()
    return renderer.render_template(template_name, context)

def render_cypher_query(query_type: str, **kwargs) -> str:
    """
    Render a Cypher query template.
    
    Parameters
    ----------
    query_type : str
        Type of query to render (e.g., "create_node", "search_vector").
    **kwargs : Dict[str, Any]
        Additional context for rendering the template.
    
    Returns
    -------
    str
        Rendered Cypher query.
    """
    renderer = JinjaRenderer()
    return renderer.render_cypher_query(query_type, **kwargs)

def render_graph_visualization(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], 
                              node_types: List[Dict[str, Any]]) -> str:
    """
    Render a graph visualization template.
    
    Parameters
    ----------
    nodes : List[Dict[str, Any]]
        List of nodes to visualize.
    edges : List[Dict[str, Any]]
        List of edges to visualize.
    node_types : List[Dict[str, Any]]
        List of node types for the legend.
    
    Returns
    -------
    str
        Rendered HTML for graph visualization.
    """
    renderer = JinjaRenderer()
    return renderer.render_graph_visualization(nodes, edges, node_types)

def render_test_template(imports: List[str], tests: List[Dict[str, Any]], 
                       class_under_test: Optional[Dict[str, Any]] = None,
                       fixtures: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Render a test template.
    
    Parameters
    ----------
    imports : List[str]
        List of import statements.
    tests : List[Dict[str, Any]]
        List of test definitions.
    class_under_test : Dict[str, Any], optional
        Information about the class under test.
    fixtures : List[Dict[str, Any]], optional
        List of test fixtures.
    
    Returns
    -------
    str
        Rendered test file.
    """
    renderer = JinjaRenderer()
    return renderer.render_test_template(imports, tests, class_under_test, fixtures)

def render_docstring(docstring_type: str, summary: str, **kwargs) -> str:
    """
    Render a docstring template.
    
    Parameters
    ----------
    docstring_type : str
        Type of docstring to render (e.g., "function", "class", "module").
    summary : str
        Summary of the docstring.
    **kwargs : Dict[str, Any]
        Additional context for rendering the template.
    
    Returns
    -------
    str
        Rendered docstring.
    """
    renderer = JinjaRenderer()
    return renderer.render_docstring(docstring_type, summary, **kwargs)
