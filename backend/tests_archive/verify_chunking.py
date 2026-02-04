"""Detailed chunking verification script"""
from app.services.chunker import TextChunker

# Initialize chunker
chunker = TextChunker(chunk_size=1000, chunk_overlap=120)

# Test 1: Short text
print("=" * 70)
print("TEST 1: Short text")
print("=" * 70)
short_text = "Artificial intelligence is the simulation of human intelligence."
short_tokens = chunker.count_tokens(short_text)
short_chunks = chunker.chunk_text(short_text, source="test", title="Short")

print(f"Original text token count: {short_tokens}")
print(f"Number of chunks created: {len(short_chunks)}")
for i, chunk in enumerate(short_chunks):
    print(f"\nChunk {i}:")
    print(f"  Position: {chunk.metadata.position}")
    print(f"  Token count: {chunk.metadata.token_count}")
    print(f"  Text length: {len(chunk.text)} chars")
    print(f"  Text preview: {chunk.text[:100]}...")

# Test 2: Medium text (should be 1 chunk)
print("\n" + "=" * 70)
print("TEST 2: Medium text")
print("=" * 70)
medium_text = """Artificial intelligence (AI) is intelligence demonstrated by machines, 
in contrast to the natural intelligence displayed by humans and animals. 
Leading AI textbooks define the field as the study of intelligent agents: 
any device that perceives its environment and takes actions that maximize 
its chance of successfully achieving its goals."""
medium_tokens = chunker.count_tokens(medium_text)
medium_chunks = chunker.chunk_text(medium_text, source="test", title="Medium")

print(f"Original text token count: {medium_tokens}")
print(f"Number of chunks created: {len(medium_chunks)}")
for i, chunk in enumerate(medium_chunks):
    print(f"\nChunk {i}:")
    print(f"  Position: {chunk.metadata.position}")
    print(f"  Token count: {chunk.metadata.token_count}")

# Test 3: Generate text with known token count
print("\n" + "=" * 70)
print("TEST 3: Repeated text (5x medium)")
print("=" * 70)
repeated_text = (medium_text + " ") * 5
repeated_tokens = chunker.count_tokens(repeated_text)
repeated_chunks = chunker.chunk_text(repeated_text, source="test", title="Repeated")

print(f"Original text token count: {repeated_tokens}")
print(f"Expected chunks (with overlap): {repeated_tokens // 1000 + (1 if repeated_tokens % 1000 > 0 else 0)}")
print(f"Actual number of chunks created: {len(repeated_chunks)}")

total_chunk_tokens = 0
for i, chunk in enumerate(repeated_chunks):
    print(f"\nChunk {i}:")
    print(f"  Position: {chunk.metadata.position}")
    print(f"  Token count: {chunk.metadata.token_count}")
    print(f"  Text length: {len(chunk.text)} chars")
    print(f"  First 80 chars: {chunk.text[:80]}...")
    total_chunk_tokens += chunk.metadata.token_count

print(f"\nTotal tokens across all chunks: {total_chunk_tokens}")
print(f"Original text tokens: {repeated_tokens}")
print(f"Expected extra tokens from overlap: ~{(len(repeated_chunks) - 1) * 120}")

# Test 4: Very long text (should create many chunks)
print("\n" + "=" * 70)
print("TEST 4: Very long text (2500+ tokens)")
print("=" * 70)
long_sentences = [f"This is sentence number {i} with some additional content to make it longer." for i in range(200)]
very_long_text = " ".join(long_sentences)
very_long_tokens = chunker.count_tokens(very_long_text)
very_long_chunks = chunker.chunk_text(very_long_text, source="test", title="VeryLong")

print(f"Original text token count: {very_long_tokens}")
print(f"Number of chunks created: {len(very_long_chunks)}")

for i, chunk in enumerate(very_long_chunks):
    print(f"\nChunk {i}:")
    print(f"  Position: {chunk.metadata.position}")
    print(f"  Token count: {chunk.metadata.token_count}")
    print(f"  Should be ~1000 tokens: {'✓' if 800 <= chunk.metadata.token_count <= 1100 else '✗ WARNING'}")

# Test 5: Verify overlap
print("\n" + "=" * 70)
print("TEST 5: Verify overlap between consecutive chunks")
print("=" * 70)
if len(very_long_chunks) > 1:
    for i in range(len(very_long_chunks) - 1):
        chunk1 = very_long_chunks[i]
        chunk2 = very_long_chunks[i + 1]
        
        # Check if there's overlapping text
        chunk1_end = chunk1.text[-200:]  # Last 200 chars of chunk 1
        chunk2_start = chunk2.text[:200]  # First 200 chars of chunk 2
        
        # Simple check: see if any words from end of chunk1 appear at start of chunk2
        chunk1_words = set(chunk1_end.split())
        chunk2_words = set(chunk2_start.split())
        overlap_words = chunk1_words & chunk2_words
        
        print(f"\nChunk {i} → Chunk {i+1}:")
        print(f"  Chunk {i} ends with: ...{chunk1.text[-60:]}")
        print(f"  Chunk {i+1} starts with: {chunk2.text[:60]}...")
        print(f"  Common words in overlap region: {len(overlap_words)} words")
        print(f"  Overlap appears to exist: {'✓' if len(overlap_words) > 0 else '✗'}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
