"""Relevance Scorer for the Context Engine.

This module provides a scorer for determining the relevance of context items
to a query.

Version: 0.1.0
Created: 2025-04-26
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from augment_adam.core.errors import (
    ResourceError, wrap_error, log_error, ErrorCategory
)
from augment_adam.context_engine.context_manager import ContextItem

logger = logging.getLogger(__name__)


class RelevanceScorer:
    """Relevance Scorer for the Context Engine.
    
    This class scores the relevance of context items to a query.
    
    Attributes:
        embedding_model: The model to use for embeddings
        use_tfidf: Whether to use TF-IDF for scoring
        vectorizer: TF-IDF vectorizer
    """
    
    def __init__(
        self,
        embedding_model: Optional[Any] = None,
        use_tfidf: bool = True
    ):
        """Initialize the Relevance Scorer.
        
        Args:
            embedding_model: The model to use for embeddings
            use_tfidf: Whether to use TF-IDF for scoring
        """
        self.embedding_model = embedding_model
        self.use_tfidf = use_tfidf
        self.vectorizer = TfidfVectorizer() if use_tfidf else None
        
        logger.info("Relevance Scorer initialized")
    
    def score(
        self,
        query: str,
        items: List[ContextItem]
    ) -> List[ContextItem]:
        """Score the relevance of context items to a query.
        
        Args:
            query: The query to score relevance for
            items: The context items to score
            
        Returns:
            The context items with updated relevance scores
        """
        try:
            if not query or not items:
                return items
            
            # If embedding model is available, use it
            if self.embedding_model is not None:
                return self._score_with_embeddings(query, items)
            
            # Otherwise, use TF-IDF if enabled
            if self.use_tfidf:
                return self._score_with_tfidf(query, items)
            
            # Fall back to keyword matching
            return self._score_with_keywords(query, items)
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to score relevance",
                category=ErrorCategory.RESOURCE,
                details={"query": query},
            )
            log_error(error, logger=logger)
            return items
    
    def _score_with_embeddings(
        self,
        query: str,
        items: List[ContextItem]
    ) -> List[ContextItem]:
        """Score relevance using embeddings.
        
        Args:
            query: The query to score relevance for
            items: The context items to score
            
        Returns:
            The context items with updated relevance scores
        """
        # This is a placeholder for actual embedding-based scoring
        # In a real implementation, use the embedding model to compute
        # embeddings for the query and items, then compute similarity
        
        # For now, fall back to TF-IDF
        return self._score_with_tfidf(query, items)
    
    def _score_with_tfidf(
        self,
        query: str,
        items: List[ContextItem]
    ) -> List[ContextItem]:
        """Score relevance using TF-IDF.
        
        Args:
            query: The query to score relevance for
            items: The context items to score
            
        Returns:
            The context items with updated relevance scores
        """
        # Extract content from items
        contents = [item.content for item in items]
        
        # Add query to contents for vectorization
        all_texts = [query] + contents
        
        # Fit and transform
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Get query vector (first row)
        query_vector = tfidf_matrix[0:1]
        
        # Get content vectors (remaining rows)
        content_vectors = tfidf_matrix[1:]
        
        # Compute cosine similarity
        similarities = cosine_similarity(query_vector, content_vectors)[0]
        
        # Update relevance scores
        for i, item in enumerate(items):
            # Combine with existing relevance score
            item.relevance = (item.relevance + similarities[i]) / 2
        
        return items
    
    def _score_with_keywords(
        self,
        query: str,
        items: List[ContextItem]
    ) -> List[ContextItem]:
        """Score relevance using keyword matching.
        
        Args:
            query: The query to score relevance for
            items: The context items to score
            
        Returns:
            The context items with updated relevance scores
        """
        # Extract keywords from query
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        
        # Score each item
        for item in items:
            content_words = set(re.findall(r'\b\w+\b', item.content.lower()))
            
            # Calculate Jaccard similarity
            if not query_words or not content_words:
                similarity = 0.0
            else:
                intersection = len(query_words.intersection(content_words))
                union = len(query_words.union(content_words))
                similarity = intersection / union
            
            # Combine with existing relevance score
            item.relevance = (item.relevance + similarity) / 2
        
        return items
