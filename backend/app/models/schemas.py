"""Pydantic schemas for request/response validation"""
from typing import List, Optional
from pydantic import BaseModel, Field


# Ingest Endpoints
class ChunkDetail(BaseModel):
    """Detail of a single chunk with metadata"""
    text: str = Field(..., description="Chunk text content")
    source: str = Field(..., description="Source identifier")
    title: Optional[str] = Field(None, description="Document title")
    section: Optional[str] = Field(None, description="Section name")
    position: int = Field(..., description="Chunk position in document")
    token_count: int = Field(..., description="Number of tokens in chunk")


class IngestRequest(BaseModel):
    """Request model for ingesting text"""
    text: str = Field(..., min_length=1, description="Text content to ingest")
    title: Optional[str] = Field(None, description="Optional title for the document")
    source: Optional[str] = Field(None, description="Optional source identifier")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Artificial intelligence is transforming various industries...",
                    "title": "AI Overview",
                    "source": "user_input"
                }
            ]
        }
    }


class IngestResponse(BaseModel):
    """Response model for ingest endpoint"""
    success: bool = Field(..., description="Whether ingestion was successful")
    message: str = Field(..., description="Status message")
    chunk_count: int = Field(..., description="Number of chunks created")
    document_id: Optional[str] = Field(None, description="Unique identifier for the document")
    chunks: Optional[List[ChunkDetail]] = Field(None, description="Detailed chunk information")


# Query Endpoints
class Citation(BaseModel):
    """Citation information for a source"""
    citation_number: int = Field(..., description="Citation number [1], [2], etc.")
    text: str = Field(..., description="Source text snippet")
    source: Optional[str] = Field(None, description="Source identifier")
    title: Optional[str] = Field(None, description="Document title")
    position: Optional[int] = Field(None, description="Chunk position in document")


class QueryRequest(BaseModel):
    """Request model for querying"""
    query: str = Field(..., min_length=1, description="Query text")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of results to return")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "What is artificial intelligence?",
                    "top_k": 5
                }
            ]
        }
    }


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    answer: str = Field(..., description="Generated answer with inline citations")
    citations: List[Citation] = Field(default_factory=list, description="List of citations")
    retrieved_chunks: int = Field(..., description="Number of chunks retrieved")
    latency_ms: float = Field(..., description="Request processing time in milliseconds")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "answer": "Artificial intelligence is a branch of computer science [1].",
                    "citations": [
                        {
                            "citation_number": 1,
                            "text": "AI is a branch of computer science...",
                            "source": "user_input",
                            "title": "AI Overview",
                            "position": 0
                        }
                    ],
                    "retrieved_chunks": 5,
                    "latency_ms": 250.5
                }
            ]
        }
    }
