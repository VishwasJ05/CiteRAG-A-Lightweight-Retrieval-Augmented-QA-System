"""Reranking service using Jina Reranker API"""
import os
from typing import List, Dict, Any
import requests
import time


class RerankerService:
    """
    Service for reranking retrieved chunks using Jina Reranker API.
    
    Reranking improves relevance by sorting chunks based on a more sophisticated
    ranking model that considers query-chunk semantic alignment.
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = "jina-reranker-v2-base-multilingual",
        top_k: int = 5,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize reranker service.
        
        Args:
            api_key: Jina API key (defaults to env variable)
            model: Reranker model to use
            top_k: Number of top chunks to return after reranking
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        if not self.api_key:
            raise ValueError("Jina API key not provided and JINA_API_KEY env variable not set")
        
        self.model = model
        self.top_k = top_k
        self.api_url = "https://api.jina.ai/v1/rerank"
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def rerank(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Rerank chunks based on relevance to query using Jina Reranker.
        
        Args:
            query: User query text
            chunks: List of chunks to rerank with format:
                    [{"id": "...", "text": "...", "metadata": {...}, "score": 0.5}, ...]
            top_k: Number of top chunks to return (overrides default)
            
        Returns:
            Dictionary containing:
            - reranked_chunks: List of reranked chunks with new scores
            - rerank_scores: List of reranker scores (before filtering)
            - count: Number of chunks after reranking (top_k)
            - metadata: Reranking metadata
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if not chunks:
            raise ValueError("No chunks to rerank")
        
        top_k = top_k or self.top_k
        
        # Extract texts for reranking
        texts = [chunk["text"] for chunk in chunks]
        
        print(f"[Reranking] Reranking {len(chunks)} chunks for query: '{query[:50]}...'")
        
        for attempt in range(self.max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "query": query,
                    "documents": [{"text": text} for text in texts],
                    "top_k": len(chunks)  # Get scores for all, then filter
                }
                
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                
                # Parse reranker response
                results = response.json()
                
                # Reorder chunks based on reranker scores
                reranked = []
                all_scores = []
                
                for result in results.get("results", []):
                    idx = result["index"]
                    score = result["relevance_score"]
                    all_scores.append(score)
                    
                    # Reconstruct chunk with new reranker score
                    reranked_chunk = chunks[idx].copy()
                    reranked_chunk["reranker_score"] = score
                    reranked.append(reranked_chunk)
                
                # Sort by reranker score (descending)
                reranked = sorted(reranked, key=lambda x: x["reranker_score"], reverse=True)
                
                # Filter to top_k
                final_chunks = reranked[:top_k]
                
                # Log comparison
                print(f"[Reranking] Retrieved top-{len(chunks)}, reranked to top-{len(final_chunks)}")
                for i, chunk in enumerate(final_chunks, 1):
                    retrieval_score = chunk.get("score", 0)
                    reranker_score = chunk.get("reranker_score", 0)
                    improvement = reranker_score - retrieval_score
                    print(f"  [{i}] Retrieval: {retrieval_score:.4f} → Reranker: {reranker_score:.4f} "
                          f"(+{improvement:+.4f}) | Text: {chunk['text'][:60]}...")
                
                return {
                    "reranked_chunks": final_chunks,
                    "rerank_scores": all_scores,
                    "count": len(final_chunks),
                    "metadata": {
                        "model": self.model,
                        "original_count": len(chunks),
                        "final_count": len(final_chunks),
                        "top_k": top_k
                    }
                }
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"[Reranking] Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    # Fallback: return original chunks if reranking fails
                    print(f"[Reranking] Failed after {self.max_retries} attempts, using retrieval scores as fallback")
                    return {
                        "reranked_chunks": chunks[:top_k],
                        "rerank_scores": [],
                        "count": min(len(chunks), top_k),
                        "metadata": {
                            "model": self.model,
                            "fallback": True,
                            "error": str(e)
                        }
                    }
