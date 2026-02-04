"""LLM service for generating grounded answers with citations using Groq API"""
import os
import re
from typing import List, Dict, Any, Tuple
from groq import Groq


class LLMService:
    """
    Service for generating grounded answers with inline citations using Groq LLM.
    
    Generates answers based ONLY on provided source chunks and includes inline citations [1], [2], etc.
    Citations are extracted from the LLM response and mapped back to source metadata.
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.3,
        max_tokens: int = 1024,
        max_retries: int = 3
    ):
        """
        Initialize LLM service.
        
        Args:
            api_key: Groq API key (defaults to env variable)
            model: Groq model to use (llama-3.1-70b-versatile, mixtral-8x7b-32768, etc.)
            temperature: Model temperature (0.0 = deterministic, 1.0 = random)
            max_tokens: Maximum tokens in response
            max_retries: Maximum number of retry attempts
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not provided and GROQ_API_KEY env variable not set")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
    
    def generate_answer(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        max_tokens: int = None
    ) -> Dict[str, Any]:
        """
        Generate a grounded answer based on provided chunks with inline citations.
        
        Args:
            query: User query
            chunks: List of top-k reranked chunks with format:
                    [{"id": "...", "text": "...", "metadata": {...}, "reranker_score": 0.8}, ...]
            max_tokens: Maximum tokens in response (overrides default)
            
        Returns:
            Dictionary containing:
            - answer: Generated answer text with inline citations [1], [2], etc.
            - citations: List of citation objects with source metadata
            - chunk_count: Number of chunks used
            - model: Model used for generation
            - metadata: Generation metadata (temperature, tokens)
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if not chunks:
            return {
                "answer": "No relevant information found in the provided sources.",
                "citations": [],
                "chunk_count": 0,
                "model": self.model,
                "metadata": {"error": "No chunks provided"}
            }
        
        max_tokens = max_tokens or self.max_tokens
        
        # Construct numbered sources for the prompt
        sources_text = self._format_sources(chunks)
        
        # Create grounded prompt
        prompt = self._construct_prompt(query, sources_text)
        
        print(f"[LLM] Generating answer for query: '{query[:60]}...'")
        print(f"[LLM] Using {len(chunks)} sources with {len(sources_text)} chars")
        
        for attempt in range(self.max_retries):
            try:
                # Call Groq API using chat.completions
                message = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=self.temperature,
                    max_tokens=max_tokens
                )
                
                # Extract answer from response
                answer_text = message.choices[0].message.content.strip()
                
                # Extract citations from answer
                citations = self._extract_citations(answer_text, chunks)
                
                print(f"[LLM] Generated answer with {len(citations)} citations")
                for i, citation in enumerate(citations, 1):
                    source_metadata = citation.get("metadata", {})
                    source_info = source_metadata.get("source", "Unknown")
                    section = source_metadata.get("section", "")
                    if section:
                        source_info += f" ({section})"
                    print(f"  [{i}] {source_info} | Score: {citation.get('reranker_score', 0):.4f}")
                
                return {
                    "answer": answer_text,
                    "citations": citations,
                    "chunk_count": len(chunks),
                    "model": self.model,
                    "metadata": {
                        "temperature": self.temperature,
                        "max_tokens": max_tokens,
                        "tokens_used": message.usage.completion_tokens if hasattr(message, 'usage') else 0
                    }
                }
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"[LLM] Attempt {attempt + 1} failed: {e}. Retrying...")
                else:
                    # Fallback response
                    print(f"[LLM] Failed after {self.max_retries} attempts, returning no-answer fallback")
                    return {
                        "answer": "I apologize, but I encountered an error while processing your query. Please try again.",
                        "citations": [],
                        "chunk_count": len(chunks),
                        "model": self.model,
                        "metadata": {
                            "error": str(e),
                            "fallback": True
                        }
                    }
    
    def _format_sources(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format chunks as numbered sources for the prompt.
        
        Args:
            chunks: List of chunks
            
        Returns:
            Formatted sources text like "[1] Source title\nText...\n\n[2] Source title\n..."
        """
        sources = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            title = metadata.get("title", "Source")
            section = metadata.get("section", "")
            text = chunk.get("text", "")
            
            # Build source header
            source_header = f"[{i}] {title}"
            if section:
                source_header += f" - {section}"
            
            sources.append(f"{source_header}\n{text}")
        
        return "\n\n".join(sources)
    
    def _construct_prompt(self, query: str, sources_text: str) -> str:
        """
        Construct the grounded prompt for the LLM.
        
        Args:
            query: User query
            sources_text: Formatted source text with numbered chunks
            
        Returns:
            Complete prompt with instructions and sources
        """
        prompt = f"""You are a helpful AI assistant. Answer the question based on the provided sources below.

IMPORTANT RULES:
1. Base your answer primarily on the numbered sources [1], [2], etc.
2. Include citations using [1], [2], etc. after sentences that reference a source.
3. Synthesize information across multiple sources when relevant.
4. If the sources provide partial information, answer what you can and note any gaps.
5. Only if the sources contain NO relevant information at all, say "I cannot find this information in the provided sources."
6. Be concise, accurate, and helpful.

SOURCES:
{sources_text}

QUESTION: {query}

ANSWER:"""
        return prompt
    
    def _extract_citations(
        self,
        answer_text: str,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract citation numbers from answer and map to source chunks.
        
        Args:
            answer_text: Generated answer text with citations [1], [2], etc.
            chunks: List of source chunks (in order)
            
        Returns:
            List of cited chunks with citation numbers and metadata
        """
        # Find all citation patterns like [1], [2], etc.
        citation_pattern = r'\[(\d+)\]'
        citation_numbers = re.findall(citation_pattern, answer_text)
        
        # Convert to set to get unique citations in order of appearance
        cited_indices = []
        seen = set()
        for num_str in citation_numbers:
            num = int(num_str)
            if num not in seen:
                cited_indices.append(num)
                seen.add(num)
        
        # Map to chunks (citations are 1-indexed)
        citations = []
        for citation_num in cited_indices:
            chunk_idx = citation_num - 1
            if 0 <= chunk_idx < len(chunks):
                citation = chunks[chunk_idx].copy()
                citation["citation_number"] = citation_num
                citations.append(citation)
        
        return citations
