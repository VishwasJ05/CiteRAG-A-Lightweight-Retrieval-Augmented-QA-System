"""Text chunking service with token-based limits and overlap"""
import re
import tiktoken
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ChunkMetadata:
    """Metadata for a text chunk"""
    source: str
    title: Optional[str]
    section: Optional[str]
    position: int
    token_count: int


@dataclass
class TextChunk:
    """A chunk of text with metadata"""
    text: str
    metadata: ChunkMetadata


class TextChunker:
    """
    Hybrid sentence-based chunker with token limits.
    
    Strategy:
    - Split text into sentences
    - Group sentences into chunks of ~1000 tokens
    - Add 12% overlap (120 tokens) between consecutive chunks
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 120,
        encoding_name: str = "cl100k_base"  # Used by GPT-4 and text-embedding-3
    ):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target number of tokens per chunk
            chunk_overlap: Number of tokens to overlap between chunks
            encoding_name: Tiktoken encoding to use for token counting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoder = tiktoken.get_encoding(encoding_name)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.encoder.encode(text))
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex.
        
        Handles common sentence endings: . ! ?
        Preserves sentence-ending punctuation.
        """
        # Pattern matches sentence boundaries
        # Looks for . ! ? followed by space and capital letter, or end of string
        pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$'
        
        sentences = re.split(pattern, text)
        
        # Filter out empty strings and strip whitespace
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def chunk_text(
        self,
        text: str,
        source: str = "user_input",
        title: Optional[str] = None,
        section: Optional[str] = None
    ) -> List[TextChunk]:
        """
        Chunk text into overlapping segments.
        
        Args:
            text: Text to chunk
            source: Source identifier for metadata
            title: Optional document title
            section: Optional section name
            
        Returns:
            List of TextChunk objects with metadata
        """
        if not text.strip():
            return []
        
        # Split into sentences
        sentences = self.split_into_sentences(text)
        
        if not sentences:
            # Fallback: treat entire text as one sentence
            sentences = [text]
        
        chunks = []
        current_chunk_sentences = []
        current_token_count = 0
        position = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # If single sentence exceeds chunk_size, split it as its own chunk
            if sentence_tokens > self.chunk_size:
                # Save current chunk if it exists
                if current_chunk_sentences:
                    chunk_text = " ".join(current_chunk_sentences)
                    chunks.append(TextChunk(
                        text=chunk_text,
                        metadata=ChunkMetadata(
                            source=source,
                            title=title,
                            section=section,
                            position=position,
                            token_count=current_token_count
                        )
                    ))
                    position += 1
                    current_chunk_sentences = []
                    current_token_count = 0
                
                # Add oversized sentence as its own chunk
                chunks.append(TextChunk(
                    text=sentence,
                    metadata=ChunkMetadata(
                        source=source,
                        title=title,
                        section=section,
                        position=position,
                        token_count=sentence_tokens
                    )
                ))
                position += 1
                continue
            
            # Check if adding this sentence would exceed chunk_size
            potential_token_count = current_token_count + sentence_tokens
            
            if potential_token_count > self.chunk_size and current_chunk_sentences:
                # Save current chunk
                chunk_text = " ".join(current_chunk_sentences)
                chunks.append(TextChunk(
                    text=chunk_text,
                    metadata=ChunkMetadata(
                        source=source,
                        title=title,
                        section=section,
                        position=position,
                        token_count=current_token_count
                    )
                ))
                position += 1
                
                # Start new chunk with overlap
                # Keep sentences from the end that fit within overlap size
                overlap_sentences = []
                overlap_tokens = 0
                
                for s in reversed(current_chunk_sentences):
                    s_tokens = self.count_tokens(s)
                    if overlap_tokens + s_tokens <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break
                
                current_chunk_sentences = overlap_sentences
                current_token_count = overlap_tokens
            
            # Add sentence to current chunk
            current_chunk_sentences.append(sentence)
            current_token_count += sentence_tokens
        
        # Add final chunk if it exists
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append(TextChunk(
                text=chunk_text,
                metadata=ChunkMetadata(
                    source=source,
                    title=title,
                    section=section,
                    position=position,
                    token_count=current_token_count
                )
            ))
        
        return chunks
    
    def chunk_to_dict(self, chunk: TextChunk) -> Dict[str, Any]:
        """Convert TextChunk to dictionary format."""
        return {
            "text": chunk.text,
            "metadata": {
                "source": chunk.metadata.source,
                "title": chunk.metadata.title,
                "section": chunk.metadata.section,
                "position": chunk.metadata.position,
                "token_count": chunk.metadata.token_count
            }
        }
