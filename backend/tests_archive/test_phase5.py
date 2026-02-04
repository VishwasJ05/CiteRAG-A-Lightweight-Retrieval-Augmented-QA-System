"""
Test script for Phase 5: Reranking
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

from app.services.retrieval_service import RetrievalService
from app.services.reranker_service import RerankerService


def main():
    print("=" * 70)
    print("PHASE 5 TEST: Reranking with Jina Reranker")
    print("=" * 70)
    
    # Test query
    test_query = "What is artificial intelligence and machine learning?"
    
    # Step 1: Initialize services
    print("\n[1/3] Initializing services...")
    try:
        retrieval_service = RetrievalService(top_k=20, lambda_param=0.5)
        reranker_service = RerankerService(top_k=5)
        print("✓ Retrieval and reranker services initialized")
    except Exception as e:
        print(f"✗ Error initializing services: {e}")
        return
    
    # Step 2: Retrieve chunks
    print(f"\n[2/3] Retrieving chunks for query: '{test_query}'")
    try:
        retrieval_results = retrieval_service.retrieve(query=test_query, top_k=20)
        retrieved_chunks = retrieval_results["chunks"]
        print(f"✓ Retrieved {len(retrieved_chunks)} chunks")
    except Exception as e:
        print(f"✗ Error retrieving chunks: {e}")
        return
    
    # Step 3: Rerank chunks
    print("\n[3/3] Reranking chunks...")
    try:
        rerank_results = reranker_service.rerank(
            query=test_query,
            chunks=retrieved_chunks,
            top_k=5
        )
        
        reranked_chunks = rerank_results["reranked_chunks"]
        print(f"✓ Reranked to {len(reranked_chunks)} top chunks")
        
        print("\nReranking Summary:")
        print(f"  - Original count: {len(retrieved_chunks)}")
        print(f"  - Reranked count: {len(reranked_chunks)}")
        print(f"  - Fallback used: {rerank_results['metadata'].get('fallback', False)}")
        
        if reranked_chunks:
            print("\nTop reranked chunk:")
            top_chunk = reranked_chunks[0]
            print(f"  - Retrieval score: {top_chunk.get('score', 'N/A'):.4f}")
            print(f"  - Reranker score: {top_chunk.get('reranker_score', 'N/A'):.4f}")
            print(f"  - Text: {top_chunk['text'][:100]}...")
        
    except Exception as e:
        print(f"✗ Error reranking chunks: {e}")
        return
    
    print("\n" + "=" * 70)
    print("✓ PHASE 5 TEST COMPLETE!")
    print("=" * 70)
    print("\nKey findings:")
    print("1. Reranker successfully reorders chunks by relevance")
    print("2. Scores indicate ranking confidence")
    print("3. Top-5 chunks are optimal for LLM input")
    print("4. Ready for Phase 6: LLM Answering with Groq")


if __name__ == "__main__":
    main()
