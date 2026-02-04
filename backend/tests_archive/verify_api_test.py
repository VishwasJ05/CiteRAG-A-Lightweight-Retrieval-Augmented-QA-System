"""Verify the actual test we ran via API"""
from app.services.chunker import TextChunker
import json

# Load the test file we used
with open('test_long_text.json', 'r') as f:
    data = json.load(f)

original_text = data['text']
chunker = TextChunker(chunk_size=1000, chunk_overlap=120)

print("=" * 70)
print("VERIFYING ACTUAL API TEST")
print("=" * 70)

# Test 1: Original text
print("\nOriginal text from test_long_text.json:")
original_tokens = chunker.count_tokens(original_text)
original_chunks = chunker.chunk_text(original_text, source="test", title="Original")
print(f"  Token count: {original_tokens}")
print(f"  Expected chunks: {len(original_chunks)}")
print(f"  Chunks created: {len(original_chunks)}")

# Test 2: Repeated 5 times (what we actually tested)
print("\nRepeated 5 times (actual API test):")
repeated_text = (original_text + " ") * 5
repeated_tokens = chunker.count_tokens(repeated_text)
repeated_chunks = chunker.chunk_text(repeated_text, source="multi_chunk_test", title="Very Long Document")

print(f"  Token count: {repeated_tokens}")
print(f"  Chunks created: {len(repeated_chunks)}")
print(f"\n  Detailed breakdown:")

for i, chunk in enumerate(repeated_chunks):
    print(f"\n  Chunk {i}:")
    print(f"    Position: {chunk.metadata.position}")
    print(f"    Tokens: {chunk.metadata.token_count}")
    print(f"    Characters: {len(chunk.text)}")
    
# Calculate expected chunks
print(f"\n" + "=" * 70)
print("MATH VERIFICATION:")
print("=" * 70)
print(f"Total tokens: {repeated_tokens}")
print(f"Chunk size: 1000 tokens")
print(f"Overlap: 120 tokens")
print(f"\nExpected calculation:")
print(f"  Chunk 1: tokens 0-1000 (1000 tokens)")
print(f"  Chunk 2: tokens 880-1880 (1000 tokens, starts at 1000-120)")
print(f"  Chunk 3: tokens 1760-2760 (1000 tokens, starts at 1880-120)")

remaining = repeated_tokens
chunk_start = 0
expected_chunks = 0
print(f"\nStep-by-step calculation:")
while remaining > 0:
    expected_chunks += 1
    chunk_end = min(chunk_start + 1000, repeated_tokens)
    chunk_size = chunk_end - chunk_start
    print(f"  Chunk {expected_chunks}: starts at token {chunk_start}, ends at {chunk_end} ({chunk_size} tokens)")
    
    if chunk_end >= repeated_tokens:
        break
    
    # Next chunk starts with overlap
    chunk_start = chunk_end - 120
    remaining = repeated_tokens - chunk_start

print(f"\nExpected chunks from math: {expected_chunks}")
print(f"Actual chunks from chunker: {len(repeated_chunks)}")
print(f"Match: {'✓ CORRECT' if expected_chunks == len(repeated_chunks) else '✗ MISMATCH'}")
