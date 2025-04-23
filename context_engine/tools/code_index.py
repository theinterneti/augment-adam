"""Code indexing tool for the context engine."""

import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from context_engine.db.redis_client import redis_client
from context_engine.db.neo4j_client import neo4j_client
from context_engine.db.embedding import embedding_model

class CodeIndexRequest(BaseModel):
    """Code index request model."""
    
    code: str = Field(..., description="The code to index")
    file_path: str = Field(..., description="Path to the file")
    language: Optional[str] = Field(None, description="Programming language")
    tier: str = Field("hot", description="Storage tier (hot, warm, or cold)")
    additional_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class CodeIndexResponse(BaseModel):
    """Code index response model."""
    
    vector_id: str = Field(..., description="ID of the stored vector")
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Message about the operation")

async def code_index(request: CodeIndexRequest) -> CodeIndexResponse:
    """Index code in the database.
    
    Args:
        request: Code index request
        
    Returns:
        Code index response
    """
    import uuid
    import time
    
    # Determine language from file extension if not provided
    language = request.language
    if not language:
        ext = os.path.splitext(request.file_path)[1].lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "bash",
            ".md": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".sql": "sql",
            ".graphql": "graphql",
            ".proto": "protobuf"
        }
        language = language_map.get(ext, "text")
    
    # Generate a vector ID based on the file path
    vector_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"file://{request.file_path}"))
    
    # Generate embedding for the code
    embedding = embedding_model.encode(request.code)
    
    # Create metadata
    metadata = {
        "file_path": request.file_path,
        "language": language,
        "created_at": int(time.time()),
        "size": len(request.code)
    }
    
    # Add additional metadata if provided
    if request.additional_metadata:
        metadata.update(request.additional_metadata)
    
    # Store in the appropriate tier
    if request.tier == "hot":
        # Store in Redis with no expiration
        success = await redis_client.store_vector(
            vector_id=vector_id,
            embedding=embedding,
            metadata=metadata,
            ttl=None
        )
    elif request.tier == "warm":
        # Store in Redis with 24-hour expiration
        success = await redis_client.store_vector(
            vector_id=vector_id,
            embedding=embedding,
            metadata=metadata,
            ttl=86400  # 24 hours
        )
    elif request.tier == "cold":
        # Store in Neo4j
        success = await neo4j_client.store_vector(
            vector_id=vector_id,
            embedding=embedding,
            metadata=metadata
        )
    else:
        return CodeIndexResponse(
            vector_id=vector_id,
            status="error",
            message=f"Invalid tier: {request.tier}"
        )
    
    # Return the response
    if success:
        return CodeIndexResponse(
            vector_id=vector_id,
            status="success",
            message=f"Code indexed in {request.tier} tier"
        )
    else:
        return CodeIndexResponse(
            vector_id=vector_id,
            status="error",
            message=f"Failed to index code in {request.tier} tier"
        )
