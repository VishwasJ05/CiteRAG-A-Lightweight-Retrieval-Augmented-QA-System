#!/usr/bin/env python
"""
Phase 6: LLM Answering & Citations Test
Tests the full RAG pipeline: Retrieval → Reranking → LLM Answer Generation
"""
import os
import sys
import time
from pathlib import Path

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Load .env from backend directory
from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.retrieval_service import RetrievalService
from app.services.reranker_service import RerankerService
from app.services.llm_service import LLMService


def test_phase6_full_pipeline():
    """Test the complete RAG pipeline including LLM answer generation"""
    
    print("\n" + "="*80)
    print("PHASE 6: LLM ANSWERING & CITATIONS TEST")
    print("="*80)
    
    # Initialize services
    print("\n[Init] Initializing services...")
    retrieval = RetrievalService(top_k=20, lambda_param=0.5)
    reranker = RerankerService(top_k=5)
    llm = LLMService()
    
    # Test queries
    test_queries = [
        "What is machine learning and how does it work?",
        "Explain deep learning neural networks",
    ]
    
    for query_idx, query in enumerate(test_queries, 1):
        print(f"\n{'-'*80}")
        print(f"TEST {query_idx}: {query}")
        print(f"{'-'*80}")
        
        try:
            # Step 1: Retrieve
            print(f"\n[Step 1] Retrieving relevant chunks...")
            start_retrieval = time.time()
            retrieval_results = retrieval.retrieve(query=query, top_k=20)
            retrieval_time = time.time() - start_retrieval
            
            retrieved_chunks = retrieval_results["chunks"]
            print(f"[OK] Retrieved {len(retrieved_chunks)} chunks in {retrieval_time:.2f}s")
            
            if not retrieved_chunks:
                print("[SKIP] No chunks found, skipping to next query")
                continue
            
            # Step 2: Rerank
            print(f"\n[Step 2] Reranking chunks...")
            start_rerank = time.time()
            rerank_results = reranker.rerank(query=query, chunks=retrieved_chunks, top_k=5)
            rerank_time = time.time() - start_rerank
            
            reranked_chunks = rerank_results["reranked_chunks"]
            print(f"[OK] Reranked to {len(reranked_chunks)} chunks in {rerank_time:.2f}s")
            
            # Step 3: Generate LLM Answer
            print(f"\n[Step 3] Generating LLM answer with citations...")
            start_llm = time.time()
            llm_results = llm.generate_answer(query=query, chunks=reranked_chunks)
            llm_time = time.time() - start_llm
            
            answer = llm_results["answer"]
            citations = llm_results["citations"]
            
            print(f"[OK] Generated answer in {llm_time:.2f}s with {len(citations)} citations")
            
            # Print results
            print(f"\n{'ANSWER':-^80}")
            print(answer)
            
            if citations:
                print(f"\n{'CITATIONS':-^80}")
                for i, citation in enumerate(citations, 1):
                    metadata = citation.get("metadata", {})
                    title = metadata.get("title", "Unknown")
                    section = metadata.get("section", "N/A")
                    score = citation.get("reranker_score", 0)
                    text_preview = citation["text"][:100]
                    
                    print(f"\n[{citation.get('citation_number')}] {title} ({section})")
                    print(f"    Score: {score:.4f}")
                    print(f"    Text: {text_preview}...")
            else:
                print("\n[WARN] No citations extracted (LLM may not have used sources)")
            
            # Step 4: Summary
            print(f"\n{'SUMMARY':-^80}")
            print(f"Query: {query}")
            print(f"Retrieved: {len(retrieved_chunks)} chunks")
            print(f"Reranked to: {len(reranked_chunks)} chunks")
            print(f"Citations: {len(citations)} sources")
            print(f"Total pipeline time: {retrieval_time + rerank_time + llm_time:.2f}s")
            print(f"  - Retrieval: {retrieval_time:.2f}s")
            print(f"  - Reranking: {rerank_time:.2f}s")
            print(f"  - LLM: {llm_time:.2f}s")
            
        except Exception as e:
            print(f"\n[ERROR] Error processing query: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("PHASE 6 TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_phase6_full_pipeline()
