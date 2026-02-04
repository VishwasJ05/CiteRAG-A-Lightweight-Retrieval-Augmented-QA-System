"""Ingest router for document ingestion"""
import time
import hashlib
from fastapi import APIRouter, HTTPException
from app.models.schemas import IngestRequest, IngestResponse, ChunkDetail
from app.services.chunker import TextChunker
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore

router = APIRouter(prefix="/ingest", tags=["ingest"])

# Initialize services
chunker = TextChunker(chunk_size=1000, chunk_overlap=120)

# These will be initialized on first use (lazy loading)
embedding_service = None
vector_store = None


def get_embedding_service():
    """Get or create embedding service instance"""
    global embedding_service
    if embedding_service is None:
        embedding_service = EmbeddingService()
    return embedding_service


def get_vector_store():
    """Get or create vector store instance"""
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store


@router.post("", response_model=IngestResponse)
async def ingest_text(request: IngestRequest):
    """
    Ingest text and store it in the vector database.
    
    This endpoint:
    1. Chunks the input text using sentence-based chunking (1000 tokens, 12% overlap)
    2. Generates embeddings for each chunk using OpenAI
    3. Stores chunks with embeddings in Pinecone vector database
    
    Phase 3: Full implementation with embeddings and vector storage.
    """
    try:
        start_time = time.time()
        
        # Generate a document ID based on text hash
        doc_id = hashlib.md5(request.text.encode()).hexdigest()[:12]
        
        # Step 1: Chunk the text with metadata
        chunks = chunker.chunk_text(
            text=request.text,
            source=request.source or "user_input",
            title=request.title,
            section=None
        )
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks generated from input text")
        
        # Convert chunks to dict format
        chunk_dicts = [chunker.chunk_to_dict(chunk) for chunk in chunks]
        
        # Step 2: Generate embeddings for all chunks (batch)
        try:
            emb_service = get_embedding_service()
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = emb_service.generate_embeddings_batch(chunk_texts)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate embeddings: {str(e)}"
            )
        
        # Step 3: Upsert to Pinecone
        try:
            vec_store = get_vector_store()
            upsert_response = vec_store.upsert_chunks(chunk_dicts, embeddings)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store vectors in Pinecone: {str(e)}"
            )
        
        # Prepare response with chunk details
        chunk_details = [
            ChunkDetail(
                text=chunk.text,
                source=chunk.metadata.source,
                title=chunk.metadata.title,
                section=chunk.metadata.section,
                position=chunk.metadata.position,
                token_count=chunk.metadata.token_count
            )
            for chunk in chunks
        ]
        
        elapsed_time = time.time() - start_time
        
        return IngestResponse(
            success=True,
            message=f"Successfully ingested {len(chunks)} chunks. Embedded and stored in Pinecone.",
            chunk_count=len(chunks),
            document_id=doc_id,
            chunks=chunk_details
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest text: {str(e)}"
        )
