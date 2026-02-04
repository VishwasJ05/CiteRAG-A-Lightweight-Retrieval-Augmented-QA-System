"""Retrieval service for semantic search with MMR (Maximal Marginal Relevance)"""
import os
from typing import List, Dict, Any
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore


class RetrievalService:
    """
    Service for retrieving relevant chunks using MMR (Maximal Marginal Relevance).
    
    MMR balances relevance (similarity to query) with diversity (dissimilarity to already-selected chunks).
    This prevents retrieving many similar chunks and ensures diverse perspectives.
    """
    
    def __init__(
        self,
        top_k: int = 20,
        lambda_param: float = 0.5
    ):
        """
        Initialize retrieval service.
        
        Args:
            top_k: Number of chunks to retrieve
            lambda_param: MMR parameter (0-1)
                - 0 = maximize diversity only
                - 0.5 = balance relevance and diversity (recommended)
                - 1 = maximize relevance only
        """
        self.top_k = top_k
        self.lambda_param = lambda_param
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        namespace: str = ""
    ) -> Dict[str, Any]:
        """
        Retrieve relevant chunks for a query using MMR.
        
        Args:
            query: User query text
            top_k: Number of chunks to retrieve (overrides default)
            namespace: Pinecone namespace
            
        Returns:
            Dictionary containing:
            - chunks: List of retrieved chunks with metadata and scores
            - query_embedding: The query embedding vector
            - count: Number of chunks retrieved
            - metadata: Retrieval metadata (lambda used, etc.)
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        top_k = top_k or self.top_k
        
        # Step 1: Embed the query using same model as ingestion
        print(f"[Retrieval] Embedding query: '{query[:50]}...'")
        query_embedding = self.embedding_service.generate_embedding(query)
        
        # Step 2: Query Pinecone with MMR
        print(f"[Retrieval] Querying Pinecone with MMR (top_k={top_k}, lambda={self.lambda_param})")
        results = self.vector_store.query_with_mmr(
            query_embedding=query_embedding,
            top_k=top_k,
            lambda_param=self.lambda_param,
            namespace=namespace
        )
        
        # Step 3: Format and log results
        chunks = []
        for match in results.matches:
            chunk = {
                "id": match.id,
                "text": match.metadata.get("text", ""),
                "score": match.score,
                "metadata": {
                    "source": match.metadata.get("source"),
                    "title": match.metadata.get("title"),
                    "position": match.metadata.get("position"),
                    "token_count": match.metadata.get("token_count")
                }
            }
            chunks.append(chunk)
            print(f"  [{len(chunks)}] Score: {match.score:.4f} | Pos: {match.metadata.get('position')} | "
                  f"Tokens: {match.metadata.get('token_count')} | Text: {match.metadata.get('text')[:60]}...")
        
        return {
            "chunks": chunks,
            "query_embedding": query_embedding,
            "count": len(chunks),
            "metadata": {
                "lambda": self.lambda_param,
                "top_k_requested": top_k,
                "top_k_retrieved": len(chunks)
            }
        }
    
    def format_chunks_for_llm(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks for LLM input with source numbering.
        
        Args:
            chunks: List of retrieved chunks
            
        Returns:
            Formatted string with numbered sources
        """
        formatted = "\n".join([
            f"[{i+1}] (Score: {chunk['score']:.2f}) {chunk['text']}"
            for i, chunk in enumerate(chunks)
        ])
        return formatted
