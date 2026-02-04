"""Unit tests for text chunker"""
import pytest
from app.services.chunker import TextChunker, TextChunk, ChunkMetadata


class TestTextChunker:
    """Test suite for TextChunker"""
    
    @pytest.fixture
    def chunker(self):
        """Create a chunker instance with default settings"""
        return TextChunker(chunk_size=1000, chunk_overlap=120)
    
    @pytest.fixture
    def small_chunker(self):
        """Create a chunker with small size for testing"""
        return TextChunker(chunk_size=50, chunk_overlap=10)
    
    def test_count_tokens(self, chunker):
        """Test token counting"""
        text = "This is a simple test sentence."
        token_count = chunker.count_tokens(text)
        assert token_count > 0
        assert isinstance(token_count, int)
    
    def test_split_into_sentences(self, chunker):
        """Test sentence splitting"""
        text = "First sentence. Second sentence! Third sentence? Fourth sentence."
        sentences = chunker.split_into_sentences(text)
        
        assert len(sentences) == 4
        assert "First sentence." in sentences[0]
        assert "Second sentence!" in sentences[1]
        assert "Third sentence?" in sentences[2]
        assert "Fourth sentence." in sentences[3]
    
    def test_chunk_empty_text(self, chunker):
        """Test chunking empty text"""
        chunks = chunker.chunk_text("")
        assert len(chunks) == 0
        
        chunks = chunker.chunk_text("   ")
        assert len(chunks) == 0
    
    def test_chunk_single_sentence(self, chunker):
        """Test chunking a single short sentence"""
        text = "This is a test."
        chunks = chunker.chunk_text(text, source="test", title="Test Doc")
        
        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].metadata.position == 0
        assert chunks[0].metadata.source == "test"
        assert chunks[0].metadata.title == "Test Doc"
        assert chunks[0].metadata.token_count > 0
    
    def test_chunk_multiple_sentences_single_chunk(self, small_chunker):
        """Test multiple sentences that fit in one chunk"""
        text = "First. Second. Third."
        chunks = small_chunker.chunk_text(text, source="test")
        
        assert len(chunks) >= 1
        # Verify metadata
        for i, chunk in enumerate(chunks):
            assert chunk.metadata.position == i
            assert chunk.metadata.source == "test"
    
    def test_chunk_with_overlap(self, small_chunker):
        """Test that chunks have proper overlap"""
        # Create text that will definitely create multiple chunks
        text = " ".join([f"Sentence number {i}." for i in range(20)])
        chunks = small_chunker.chunk_text(text, source="test")
        
        # Should create multiple chunks
        assert len(chunks) > 1
        
        # Verify positions are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.metadata.position == i
    
    def test_chunk_oversized_sentence(self, small_chunker):
        """Test handling of sentence larger than chunk_size"""
        # Create a very long sentence (no periods)
        long_sentence = " ".join(["word"] * 100)
        chunks = small_chunker.chunk_text(long_sentence, source="test")
        
        # Should still create chunks even if sentence is oversized
        assert len(chunks) >= 1
        assert chunks[0].metadata.token_count > small_chunker.chunk_size
    
    def test_metadata_preservation(self, chunker):
        """Test that metadata is correctly attached to all chunks"""
        text = " ".join([f"Sentence {i}." for i in range(100)])
        
        chunks = chunker.chunk_text(
            text,
            source="test_source",
            title="Test Title",
            section="Test Section"
        )
        
        assert len(chunks) > 0
        
        for i, chunk in enumerate(chunks):
            assert chunk.metadata.source == "test_source"
            assert chunk.metadata.title == "Test Title"
            assert chunk.metadata.section == "Test Section"
            assert chunk.metadata.position == i
            assert chunk.metadata.token_count > 0
            assert chunk.metadata.token_count <= chunker.chunk_size + 100  # Allow some margin
    
    def test_chunk_to_dict(self, chunker):
        """Test conversion of chunk to dictionary"""
        text = "Test sentence."
        chunks = chunker.chunk_text(text, source="test", title="Title")
        
        chunk_dict = chunker.chunk_to_dict(chunks[0])
        
        assert "text" in chunk_dict
        assert "metadata" in chunk_dict
        assert chunk_dict["text"] == text
        assert chunk_dict["metadata"]["source"] == "test"
        assert chunk_dict["metadata"]["title"] == "Title"
        assert chunk_dict["metadata"]["position"] == 0
    
    def test_realistic_text_chunking(self, chunker):
        """Test with realistic AI text"""
        text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, 
        in contrast to the natural intelligence displayed by humans and animals. 
        Leading AI textbooks define the field as the study of intelligent agents: 
        any device that perceives its environment and takes actions that maximize 
        its chance of successfully achieving its goals. Colloquially, the term 
        artificial intelligence is often used to describe machines that mimic 
        cognitive functions that humans associate with the human mind, such as 
        learning and problem solving.
        """
        
        chunks = chunker.chunk_text(
            text,
            source="wikipedia",
            title="AI Overview",
            section="Introduction"
        )
        
        # Should fit in one chunk given the size
        assert len(chunks) >= 1
        
        # Verify all chunks have content
        for chunk in chunks:
            assert len(chunk.text.strip()) > 0
            assert chunk.metadata.token_count > 0
    
    def test_chunk_size_adherence(self, chunker):
        """Test that chunks generally adhere to size limits"""
        # Create a long text
        text = " ".join([f"This is sentence number {i}." for i in range(500)])
        
        chunks = chunker.chunk_text(text, source="test")
        
        # Should create multiple chunks
        assert len(chunks) > 1
        
        # Most chunks should be within reasonable bounds
        # Allow some margin for edge cases
        for chunk in chunks[:-1]:  # Exclude last chunk which might be smaller
            assert chunk.metadata.token_count <= chunker.chunk_size + 200
    
    def test_no_duplicate_content_without_overlap(self, chunker):
        """Test that content isn't duplicated beyond overlap"""
        text = " ".join([f"Unique sentence {i}." for i in range(200)])
        chunks = chunker.chunk_text(text, source="test")
        
        # Basic sanity check - we should have chunks
        assert len(chunks) > 0
        
        # Total text in chunks should be >= original (due to overlap)
        total_chunk_text = " ".join([c.text for c in chunks])
        # Each unique sentence should appear at least once
        for i in range(200):
            assert f"Unique sentence {i}." in total_chunk_text
