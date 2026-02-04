"""Query router for answering questions"""
import time
from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse, Citation
from app.services.retrieval_service import RetrievalService
from app.services.reranker_service import RerankerService
from app.services.llm_service import LLMService

router = APIRouter(prefix="/query", tags=["query"])

# Initialize services
retrieval_service = None
reranker_service = None
llm_service = None


def get_retrieval_service():
    """Get or create retrieval service instance"""
    global retrieval_service
    if retrieval_service is None:
        retrieval_service = RetrievalService(top_k=20, lambda_param=0.5)
    return retrieval_service


def get_reranker_service():
    """Get or create reranker service instance"""
    global reranker_service
    if reranker_service is None:
        reranker_service = RerankerService(top_k=5)
    return reranker_service


def get_llm_service():
    """Get or create LLM service instance"""
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service


@router.post("", response_model=QueryResponse)
async def query_text(request: QueryRequest):
    """
    Query the vector database and generate an answer with citations.
    
    This endpoint implements the full RAG pipeline:
    1. Embed the query (implicit in retrieval)
    2. Retrieve relevant chunks from Pinecone with MMR (Phase 4) ✓
    3. Rerank chunks using Jina Reranker (Phase 5) ✓
    4. Generate answer using Groq LLM with citations (Phase 6) ✓
    
    Pipeline: Query → Retrieval (top-20) → Reranking (top-5) → LLM Answer → Citations
    """
    try:
        start_time = time.time()
        
        # Phase 4: Retrieve relevant chunks (top-20 with MMR)
        retrieval = get_retrieval_service()
        retrieval_results = retrieval.retrieve(
            query=request.query,
            top_k=20
        )
        
        retrieved_chunks = retrieval_results["chunks"]
        print(f"[DEBUG] Retrieved {len(retrieved_chunks)} chunks for query: '{request.query[:60]}'")
        for i, chunk in enumerate(retrieved_chunks[:3], 1):  # Show first 3
            print(f"[DEBUG] Chunk {i}: {chunk['text'][:100]}... (score: {chunk.get('score', 'N/A')})")
        
        if not retrieved_chunks:
            raise HTTPException(
                status_code=404,
                detail="No relevant chunks found in the database"
            )
        
        # Phase 5: Rerank chunks to top-5
        reranker = get_reranker_service()
        rerank_results = reranker.rerank(
            query=request.query,
            chunks=retrieved_chunks,
            top_k=5
        )
        
        reranked_chunks = rerank_results["reranked_chunks"]
        print(f"[DEBUG] Reranked to {len(reranked_chunks)} chunks")
        for i, chunk in enumerate(reranked_chunks, 1):
            print(f"[DEBUG] Reranked #{i}: {chunk['text'][:100]}... (score: {chunk.get('reranker_score', 'N/A')})")
        
        # Phase 6: Generate answer using LLM with citations
        llm = get_llm_service()
        llm_results = llm.generate_answer(
            query=request.query,
            chunks=reranked_chunks
        )
        
        # Build citations from LLM results
        citations = [
            Citation(
                citation_number=citation.get("citation_number"),
                text=citation["text"],
                source=citation["metadata"].get("source"),
                title=citation["metadata"].get("title"),
                position=citation["metadata"].get("position")
            )
            for citation in llm_results["citations"]
        ]
        
        elapsed_time = time.time() - start_time
        
        return QueryResponse(
            answer=llm_results["answer"],
            citations=citations,
            retrieved_chunks=len(reranked_chunks),
            latency_ms=elapsed_time * 1000
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query: {str(e)}"
        )
