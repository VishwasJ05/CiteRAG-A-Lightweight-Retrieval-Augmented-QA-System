"""
Test script for Phase 3: Embeddings and Vector DB
"""
import sys
import os
from dotenv import load_dotenv
base_dir = os.path.dirname(__file__)
sys.path.insert(0, base_dir)
load_dotenv(dotenv_path=os.path.join(base_dir, ".env"), override=True)

from app.services.chunker import TextChunker
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore

# Sample text for testing
sample_text = """
Artificial intelligence (AI) is transforming the world. Machine learning algorithms 
can now process vast amounts of data to identify patterns and make predictions. 
Deep learning, a subset of machine learning, uses neural networks with multiple layers 
to analyze complex data. Natural language processing enables computers to understand 
and generate human language. Computer vision allows machines to interpret and analyze 
visual information from the world. AI applications range from autonomous vehicles to 
medical diagnosis, financial trading to customer service chatbots. However, AI also 
raises important ethical concerns about bias, privacy, and job displacement. 
Researchers are working on developing explainable AI systems that can provide 
transparent reasoning for their decisions. The future of AI likely involves more 
sophisticated models that can reason, plan, and adapt to new situations with minimal 
training data.
"""

def main():
    print("=" * 60)
    print("PHASE 3 TEST: Embeddings & Vector DB")
    print("=" * 60)

    # Quick environment sanity check (masked)
    jina_key = os.getenv("JINA_API_KEY", "")
    print(
        f"Jina key loaded: {bool(jina_key)} | length: {len(jina_key)}"
    )
    
    # Step 1: Chunking
    print("\n[1/3] Chunking text...")
    chunker = TextChunker()
    chunks = chunker.chunk_text(
        text=sample_text,
        source="test_document",
        title="Introduction to AI"
    )
    print(f"✓ Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"  - Chunk {i+1}: {chunk.metadata.token_count} tokens")
    
    # Step 2: Generate embeddings
    print("\n[2/3] Generating embeddings via OpenAI...")
    try:
        embedding_service = EmbeddingService()
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_service.generate_embeddings_batch(texts)
        print(f"✓ Generated {len(embeddings)} embeddings")
        print(f"  - Embedding dimension: {len(embeddings[0])}")
    except Exception as e:
        print(f"✗ Error generating embeddings: {e}")
        return
    
    # Step 3: Store in Pinecone
    print("\n[3/3] Storing vectors in Pinecone...")
    try:
        vector_store = VectorStore()
        chunk_dicts = [chunker.chunk_to_dict(chunk) for chunk in chunks]
        vector_store.upsert_chunks(chunk_dicts, embeddings)
        print(f"✓ Successfully stored {len(chunks)} vectors in Pinecone")
    except Exception as e:
        print(f"✗ Error storing in Pinecone: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✓ PHASE 3 TEST COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Verify vectors in Pinecone dashboard at https://app.pinecone.io")
    print("2. Check the 'mini-rag-index' index for uploaded vectors")
    print("3. Ready to proceed to Phase 4: Retrieval Strategy")

if __name__ == "__main__":
    main()
