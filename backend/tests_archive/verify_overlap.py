"""Detailed overlap verification"""
from app.services.chunker import TextChunker
import json

with open('test_long_text.json', 'r') as f:
    data = json.load(f)

original_text = data['text']
repeated_text = (original_text + " ") * 5

chunker = TextChunker(chunk_size=1000, chunk_overlap=120)
chunks = chunker.chunk_text(repeated_text, source="test", title="Overlap Test")

print("=" * 70)
print("OVERLAP VERIFICATION")
print("=" * 70)
print(f"\nTotal chunks: {len(chunks)}")
print(f"Expected overlap: 120 tokens between consecutive chunks")
print()

for i in range(len(chunks) - 1):
    print(f"\n{'='*70}")
    print(f"Checking overlap between Chunk {i} and Chunk {i+1}")
    print(f"{'='*70}")
    
    chunk1 = chunks[i]
    chunk2 = chunks[i+1]
    
    # Get the last ~150 tokens worth of text from chunk1
    chunk1_end = chunk1.text[-800:]
    # Get the first ~150 tokens worth of text from chunk2
    chunk2_start = chunk2.text[:800]
    
    # Find common substring
    # Start with longer substrings and work down
    overlap_found = ""
    for length in range(min(len(chunk1_end), len(chunk2_start)), 20, -1):
        for start in range(len(chunk1_end) - length + 1):
            substring = chunk1_end[start:start + length]
            if substring in chunk2_start:
                if len(substring) > len(overlap_found):
                    overlap_found = substring
                    break
        if len(overlap_found) >= 100:  # Found significant overlap
            break
    
    if overlap_found:
        overlap_tokens = chunker.count_tokens(overlap_found)
        print(f"\nOverlap found:")
        print(f"  Token count: {overlap_tokens} tokens")
        print(f"  Character count: {len(overlap_found)} chars")
        print(f"  Expected: ~120 tokens")
        print(f"  Status: {'✓ GOOD' if 80 <= overlap_tokens <= 160 else '✗ WARNING'}")
        print(f"\n  Overlap text preview:")
        print(f"  Start: {overlap_found[:80]}...")
        print(f"  End: ...{overlap_found[-80:]}")
    else:
        print(f"  ✗ No significant overlap found!")
    
    print(f"\nChunk {i} stats:")
    print(f"  Tokens: {chunk1.metadata.token_count}")
    print(f"  Last 100 chars: ...{chunk1.text[-100:]}")
    
    print(f"\nChunk {i+1} stats:")
    print(f"  Tokens: {chunk2.metadata.token_count}")
    print(f"  First 100 chars: {chunk2.text[:100]}...")

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print(f"Total text: {chunker.count_tokens(repeated_text)} tokens")
print(f"Chunks: {len(chunks)}")
print(f"Average chunk size: {sum(c.metadata.token_count for c in chunks) / len(chunks):.0f} tokens")
print(f"Expected overlap regions: {len(chunks) - 1}")
print(f"Configuration: chunk_size={chunker.chunk_size}, overlap={chunker.chunk_overlap}")
