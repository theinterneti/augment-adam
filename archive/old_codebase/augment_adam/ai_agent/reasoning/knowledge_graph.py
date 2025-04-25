"""Knowledge Graph for the AI Agent.

This module implements a knowledge graph for organizing information.

Version: 0.1.0
Created: 2025-04-27
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple, Set

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """Knowledge Graph for the AI Agent.
    
    This class implements a knowledge graph for organizing information.
    
    Attributes:
        nodes: Dictionary of nodes in the graph
        edges: Dictionary of edges in the graph
        topics: Dictionary of topics and their associated nodes
    """
    
    def __init__(self):
        """Initialize the Knowledge Graph."""
        self.nodes = {}
        self.edges = {}
        self.topics = {}
        
        logger.info("Initialized Knowledge Graph")
    
    def add_knowledge(self, knowledge: Dict[str, Any]) -> str:
        """Add knowledge to the graph.
        
        Args:
            knowledge: The knowledge to add
            
        Returns:
            The ID of the added node
        """
        try:
            # Generate node ID
            node_id = f"node_{len(self.nodes) + 1}"
            
            # Create node
            node = {
                "id": node_id,
                "text": knowledge.get("text", ""),
                "topic": knowledge.get("topic", "general"),
                "confidence": knowledge.get("confidence", 1.0),
                "source": knowledge.get("source", "unknown")
            }
            
            # Add node to graph
            self.nodes[node_id] = node
            
            # Add node to topic
            topic = knowledge.get("topic", "general")
            if topic not in self.topics:
                self.topics[topic] = set()
            self.topics[topic].add(node_id)
            
            # Extract entities and create edges (placeholder)
            self._extract_and_link_entities(node_id, knowledge)
            
            logger.info(f"Added knowledge node {node_id} to topic {topic}")
            return node_id
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to add knowledge to graph",
                category=ErrorCategory.RESOURCE,
                details={},
            )
            log_error(error, logger=logger)
            return ""
    
    def _extract_and_link_entities(self, node_id: str, knowledge: Dict[str, Any]) -> None:
        """Extract entities from knowledge and link them in the graph.
        
        Args:
            node_id: The ID of the node
            knowledge: The knowledge to extract entities from
        """
        # This is a placeholder for actual entity extraction and linking
        # In a real implementation, use NLP techniques to extract entities
        
        # Simple word-based approach
        text = knowledge.get("text", "")
        words = text.split()
        
        # Extract potential entities (capitalized words)
        entities = [word for word in words if word and word[0].isupper()]
        
        # Create entity nodes and edges
        for entity in entities:
            # Check if entity node already exists
            entity_id = None
            for nid, node in self.nodes.items():
                if node.get("text", "") == entity and node.get("type", "") == "entity":
                    entity_id = nid
                    break
            
            # Create new entity node if needed
            if not entity_id:
                entity_id = f"entity_{len(self.nodes) + 1}"
                entity_node = {
                    "id": entity_id,
                    "text": entity,
                    "type": "entity",
                    "topic": knowledge.get("topic", "general")
                }
                self.nodes[entity_id] = entity_node
            
            # Create edge between knowledge node and entity node
            edge_id = f"edge_{len(self.edges) + 1}"
            edge = {
                "id": edge_id,
                "source": node_id,
                "target": entity_id,
                "type": "mentions",
                "confidence": 0.7  # Placeholder confidence
            }
            self.edges[edge_id] = edge
    
    def get_context(self, topic: str, max_nodes: int = 10) -> str:
        """Get context for a topic from the graph.
        
        Args:
            topic: The topic to get context for
            max_nodes: Maximum number of nodes to include
            
        Returns:
            The context as text
        """
        try:
            # Get nodes for the topic
            node_ids = self.topics.get(topic, set())
            
            if not node_ids:
                return f"No knowledge available for topic: {topic}"
            
            # Sort nodes by confidence
            sorted_nodes = sorted(
                [self.nodes[nid] for nid in node_ids],
                key=lambda n: n.get("confidence", 0.0),
                reverse=True
            )
            
            # Limit to max_nodes
            selected_nodes = sorted_nodes[:max_nodes]
            
            # Format context
            context = f"Knowledge Graph for {topic}:\n\n"
            
            for node in selected_nodes:
                context += f"- {node.get('text', '')}"
                if node.get("source", "") != "unknown":
                    context += f" (Source: {node.get('source', '')})"
                context += "\n"
            
            # Add related entities
            entities = self._get_related_entities(node_ids)
            if entities:
                context += f"\nRelated Entities for {topic}:\n"
                for entity in entities[:5]:  # Limit to 5 entities
                    context += f"- {entity}\n"
            
            return context
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to get context from graph",
                category=ErrorCategory.RESOURCE,
                details={"topic": topic},
            )
            log_error(error, logger=logger)
            return f"Error retrieving context for topic: {topic}"
    
    def _get_related_entities(self, node_ids: Set[str]) -> List[str]:
        """Get entities related to a set of nodes.
        
        Args:
            node_ids: The IDs of the nodes
            
        Returns:
            The related entities
        """
        entities = []
        
        # Find edges connecting to these nodes
        for edge_id, edge in self.edges.items():
            if edge.get("source", "") in node_ids:
                target_id = edge.get("target", "")
                target_node = self.nodes.get(target_id)
                
                if target_node and target_node.get("type", "") == "entity":
                    entities.append(target_node.get("text", ""))
        
        return entities
    
    def get_summary(self, topic: str) -> Dict[str, Any]:
        """Get a summary of the graph for a topic.
        
        Args:
            topic: The topic to get a summary for
            
        Returns:
            The summary
        """
        try:
            # Get nodes for the topic
            node_ids = self.topics.get(topic, set())
            
            if not node_ids:
                return {
                    "topic": topic,
                    "node_count": 0,
                    "entity_count": 0,
                    "edge_count": 0
                }
            
            # Count entities and edges
            entity_count = 0
            edge_count = 0
            
            for node_id in node_ids:
                # Count edges for this node
                for edge_id, edge in self.edges.items():
                    if edge.get("source", "") == node_id:
                        edge_count += 1
                        
                        # Check if target is an entity
                        target_id = edge.get("target", "")
                        target_node = self.nodes.get(target_id)
                        
                        if target_node and target_node.get("type", "") == "entity":
                            entity_count += 1
            
            # Create summary
            summary = {
                "topic": topic,
                "node_count": len(node_ids),
                "entity_count": entity_count,
                "edge_count": edge_count
            }
            
            return summary
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to get summary from graph",
                category=ErrorCategory.RESOURCE,
                details={"topic": topic},
            )
            log_error(error, logger=logger)
            return {
                "topic": topic,
                "error": str(error)
            }
    
    def query(self, query: str, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query the knowledge graph.
        
        Args:
            query: The query to execute
            topic: The topic to limit the query to
            
        Returns:
            The query results
        """
        try:
            # This is a placeholder for actual graph querying
            # In a real implementation, use a proper graph query language
            
            # Simple keyword-based approach
            keywords = query.lower().split()
            
            # Get nodes to search
            if topic:
                node_ids = self.topics.get(topic, set())
            else:
                node_ids = set(self.nodes.keys())
            
            # Search nodes
            results = []
            for node_id in node_ids:
                node = self.nodes[node_id]
                text = node.get("text", "").lower()
                
                # Check if any keyword is in the text
                if any(keyword in text for keyword in keywords):
                    results.append(node)
            
            logger.info(f"Query '{query}' returned {len(results)} results")
            return results
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to query graph",
                category=ErrorCategory.RESOURCE,
                details={"query": query},
            )
            log_error(error, logger=logger)
            return []
