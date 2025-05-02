"""
Unit tests for the Context Engine core functionality.

This module contains tests for the core functionality of the Context Engine,
including context retrieval, chunking, and composition.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from augment_adam.context.core.base import ContextEngine, Context, ContextType


class TestContextEngine:
    """Tests for the Context Engine."""

    def test_context_init(self):
        """Test initializing a Context."""
        context = Context(
            content="test content",
            context_type=ContextType.TEXT,
            metadata={"source": "test"},
            importance=0.8
        )

        assert context.content == "test content"
        assert context.context_type == ContextType.TEXT
        assert context.metadata == {"source": "test"}
        assert context.importance == 0.8
        assert context.id is not None

    def test_context_to_dict(self):
        """Test converting a Context to a dictionary."""
        context = Context(
            id="test_id",
            content="test content",
            context_type=ContextType.CODE,
            metadata={"source": "test.py"},
            importance=0.8
        )

        context_dict = context.to_dict()
        assert context_dict["id"] == "test_id"
        assert context_dict["content"] == "test content"
        assert context_dict["context_type"] == "CODE"
        assert context_dict["metadata"] == {"source": "test.py"}
        assert context_dict["importance"] == 0.8

    def test_context_from_dict(self):
        """Test creating a Context from a dictionary."""
        data = {
            "id": "test_id",
            "content": "test content",
            "context_type": "CODE",
            "metadata": {"source": "test.py"},
            "importance": 0.8
        }

        context = Context.from_dict(data)
        assert context.id == "test_id"
        assert context.content == "test content"
        assert context.context_type == ContextType.CODE
        assert context.metadata == {"source": "test.py"}
        assert context.importance == 0.8

    def test_context_update(self):
        """Test updating a Context."""
        context = Context(
            content="test content",
            metadata={"source": "test"}
        )

        context.update(content="updated content", metadata={"key": "value"})

        assert context.content == "updated content"
        assert context.metadata == {"source": "test", "key": "value"}

    def test_context_engine_init(self):
        """Test initializing a ContextEngine."""
        engine = ContextEngine(name="test_engine")

        assert engine.name == "test_engine"
        assert engine.contexts == {}
        assert engine.chunker is None
        assert engine.composer is None
        assert engine.retriever is None
        assert engine.storage is None

    def test_add_context(self):
        """Test adding a Context to the ContextEngine."""
        engine = ContextEngine(name="test_engine")
        context = Context(content="test content")

        context_id = engine.add_context(context)

        assert context_id == context.id
        assert context_id in engine.contexts
        assert engine.contexts[context_id] == context

    def test_get_context(self):
        """Test getting a Context from the ContextEngine."""
        engine = ContextEngine(name="test_engine")
        context = Context(id="test_id", content="test content")
        engine.add_context(context)

        retrieved_context = engine.get_context("test_id")

        assert retrieved_context == context

    def test_update_context(self):
        """Test updating a Context in the ContextEngine."""
        engine = ContextEngine(name="test_engine")
        context = Context(id="test_id", content="test content")
        engine.add_context(context)

        updated_context = engine.update_context("test_id", content="updated content")

        assert updated_context == context
        assert updated_context.content == "updated content"

    def test_remove_context(self):
        """Test removing a Context from the ContextEngine."""
        engine = ContextEngine(name="test_engine")
        context = Context(id="test_id", content="test content")
        engine.add_context(context)

        result = engine.remove_context("test_id")

        assert result is True
        assert "test_id" not in engine.contexts

    def test_chunk_content(self):
        """Test chunking content with the ContextEngine."""
        engine = ContextEngine(name="test_engine")
        chunker = MagicMock()
        chunker.chunk.return_value = [
            Context(content="chunk1"),
            Context(content="chunk2")
        ]
        engine.chunker = chunker

        chunks = engine.chunk_content("test content", ContextType.TEXT)

        assert len(chunks) == 2
        assert chunks[0].content == "chunk1"
        assert chunks[1].content == "chunk2"
        chunker.chunk.assert_called_once_with("test content", ContextType.TEXT)

    def test_compose_context(self):
        """Test composing contexts with the ContextEngine."""
        engine = ContextEngine(name="test_engine")
        composer = MagicMock()
        composer.compose.return_value = Context(content="composed content")
        engine.composer = composer

        contexts = [
            Context(content="context1"),
            Context(content="context2")
        ]

        composed = engine.compose_context(contexts)

        assert composed.content == "composed content"
        composer.compose.assert_called_once_with(contexts)

    def test_retrieve_context(self):
        """Test retrieving contexts with the ContextEngine."""
        engine = ContextEngine(name="test_engine")
        retriever = MagicMock()
        retriever.retrieve.return_value = [
            Context(content="result1"),
            Context(content="result2")
        ]
        engine.retriever = retriever

        results = engine.retrieve_context("test query")

        assert len(results) == 2
        assert results[0].content == "result1"
        assert results[1].content == "result2"
        retriever.retrieve.assert_called_once_with("test query", 10)

    def test_get_contexts_by_type(self):
        """Test getting contexts by type from the ContextEngine."""
        engine = ContextEngine(name="test_engine")
        context1 = Context(content="text content", context_type=ContextType.TEXT)
        context2 = Context(content="code content", context_type=ContextType.CODE)
        engine.add_context(context1)
        engine.add_context(context2)

        text_contexts = engine.get_contexts_by_type(ContextType.TEXT)

        assert len(text_contexts) == 1
        assert text_contexts[0] == context1

    def test_get_contexts_by_tag(self):
        """Test getting contexts by tag from the ContextEngine."""
        engine = ContextEngine(name="test_engine")
        context1 = Context(content="tagged content", tags=["test_tag"])
        context2 = Context(content="untagged content")
        engine.add_context(context1)
        engine.add_context(context2)

        tagged_contexts = engine.get_contexts_by_tag("test_tag")

        assert len(tagged_contexts) == 1
        assert tagged_contexts[0] == context1
