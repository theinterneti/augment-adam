"""
Unit tests for the Context Engine core functionality.

This module contains tests for the core functionality of the Context Engine,
including context retrieval, chunking, and composition.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from augment_adam.context_engine import ContextEngine, ContextResult, ContextQuery


class TestContextEngine:
    """Tests for the Context Engine."""

    def test_context_query_init(self):
        """Test initializing a ContextQuery."""
        query = ContextQuery(
            query="test query",
            max_results=10,
            filters={"language": "python"},
            include_code=True,
            include_metadata=True
        )
        
        assert query.query == "test query"
        assert query.max_results == 10
        assert query.filters == {"language": "python"}
        assert query.include_code is True
        assert query.include_metadata is True
    
    def test_context_result_init(self):
        """Test initializing a ContextResult."""
        result = ContextResult(
            text="test result",
            score=0.95,
            metadata={"file": "test.py", "line": 10},
            source_code="def test():\n    pass"
        )
        
        assert result.text == "test result"
        assert result.score == 0.95
        assert result.metadata == {"file": "test.py", "line": 10}
        assert result.source_code == "def test():\n    pass"
    
    def test_context_result_to_dict(self):
        """Test converting a ContextResult to a dictionary."""
        result = ContextResult(
            text="test result",
            score=0.95,
            metadata={"file": "test.py", "line": 10},
            source_code="def test():\n    pass"
        )
        
        result_dict = result.to_dict()
        assert result_dict["text"] == "test result"
        assert result_dict["score"] == 0.95
        assert result_dict["metadata"] == {"file": "test.py", "line": 10}
        assert result_dict["source_code"] == "def test():\n    pass"
    
    def test_context_engine_init(self):
        """Test initializing a ContextEngine."""
        engine = ContextEngine()
        
        assert engine.chunkers == {}
        assert engine.retrievers == {}
        assert engine.composers == {}
    
    def test_register_chunker(self):
        """Test registering a chunker."""
        engine = ContextEngine()
        chunker = MagicMock()
        chunker.name = "test_chunker"
        
        engine.register_chunker(chunker)
        
        assert "test_chunker" in engine.chunkers
        assert engine.chunkers["test_chunker"] == chunker
    
    def test_register_retriever(self):
        """Test registering a retriever."""
        engine = ContextEngine()
        retriever = MagicMock()
        retriever.name = "test_retriever"
        
        engine.register_retriever(retriever)
        
        assert "test_retriever" in engine.retrievers
        assert engine.retrievers["test_retriever"] == retriever
    
    def test_register_composer(self):
        """Test registering a composer."""
        engine = ContextEngine()
        composer = MagicMock()
        composer.name = "test_composer"
        
        engine.register_composer(composer)
        
        assert "test_composer" in engine.composers
        assert engine.composers["test_composer"] == composer
    
    @pytest.mark.asyncio
    async def test_retrieve_context(self):
        """Test retrieving context."""
        engine = ContextEngine()
        retriever = AsyncMock()
        retriever.name = "test_retriever"
        retriever.retrieve.return_value = [
            ContextResult(
                text="test result",
                score=0.95,
                metadata={"file": "test.py", "line": 10},
                source_code="def test():\n    pass"
            )
        ]
        
        engine.register_retriever(retriever)
        
        query = ContextQuery(query="test query")
        results = await engine.retrieve_context(query, retriever_name="test_retriever")
        
        assert len(results) == 1
        assert results[0].text == "test result"
        assert results[0].score == 0.95
        retriever.retrieve.assert_called_once_with(query)
    
    @pytest.mark.asyncio
    async def test_retrieve_context_with_multiple_retrievers(self):
        """Test retrieving context with multiple retrievers."""
        engine = ContextEngine()
        
        retriever1 = AsyncMock()
        retriever1.name = "test_retriever1"
        retriever1.retrieve.return_value = [
            ContextResult(
                text="result1",
                score=0.95,
                metadata={"file": "test1.py", "line": 10},
                source_code="def test1():\n    pass"
            )
        ]
        
        retriever2 = AsyncMock()
        retriever2.name = "test_retriever2"
        retriever2.retrieve.return_value = [
            ContextResult(
                text="result2",
                score=0.90,
                metadata={"file": "test2.py", "line": 20},
                source_code="def test2():\n    pass"
            )
        ]
        
        engine.register_retriever(retriever1)
        engine.register_retriever(retriever2)
        
        query = ContextQuery(query="test query")
        results = await engine.retrieve_context(query)
        
        assert len(results) == 2
        assert any(r.text == "result1" for r in results)
        assert any(r.text == "result2" for r in results)
        retriever1.retrieve.assert_called_once_with(query)
        retriever2.retrieve.assert_called_once_with(query)
    
    @pytest.mark.asyncio
    async def test_chunk_text(self):
        """Test chunking text."""
        engine = ContextEngine()
        chunker = AsyncMock()
        chunker.name = "test_chunker"
        chunker.chunk.return_value = ["chunk1", "chunk2"]
        
        engine.register_chunker(chunker)
        
        chunks = await engine.chunk_text("test text", chunker_name="test_chunker")
        
        assert len(chunks) == 2
        assert "chunk1" in chunks
        assert "chunk2" in chunks
        chunker.chunk.assert_called_once_with("test text")
    
    @pytest.mark.asyncio
    async def test_compose_context(self):
        """Test composing context."""
        engine = ContextEngine()
        composer = AsyncMock()
        composer.name = "test_composer"
        composer.compose.return_value = "composed context"
        
        engine.register_composer(composer)
        
        results = [
            ContextResult(
                text="result1",
                score=0.95,
                metadata={"file": "test1.py", "line": 10},
                source_code="def test1():\n    pass"
            ),
            ContextResult(
                text="result2",
                score=0.90,
                metadata={"file": "test2.py", "line": 20},
                source_code="def test2():\n    pass"
            )
        ]
        
        composed = await engine.compose_context(results, composer_name="test_composer")
        
        assert composed == "composed context"
        composer.compose.assert_called_once()
        assert composer.compose.call_args[0][0] == results
