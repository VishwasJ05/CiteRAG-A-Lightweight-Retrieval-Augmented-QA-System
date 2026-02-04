"""Check if there's data in Pinecone"""
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME", "mini-rag-index")
print(f"Checking index: {index_name}")
index = pc.Index(index_name)

# Get stats
stats = index.describe_index_stats()
print(f"Total vectors in index: {stats['total_vector_count']}")
print(f"Namespaces: {stats.get('namespaces', {})}")

# Try a simple query
if stats['total_vector_count'] > 0:
    # Query with a dummy vector to see what's in there
    results = index.query(
        vector=[0.1] * 1024,  # Jina v3 uses 1024 dimensions
        top_k=5,
        include_metadata=True
    )
    
    print(f"\nSample documents:")
    for i, match in enumerate(results['matches'], 1):
        text = match['metadata'].get('text', '')[:200]
        print(f"{i}. Score: {match['score']:.4f}")
        print(f"   Text: {text}...")
        print()
