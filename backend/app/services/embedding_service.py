"""Embedding generation service using Jina API"""
import os
from typing import List, Dict, Any
import requests
import time


class EmbeddingService:
    """
    Service for generating text embeddings using Jina API.
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize embedding service.
        
        Args:
            api_key: Jina API key (defaults to env variable)
            model: Embedding model to use
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        if not self.api_key:
            raise ValueError("Jina API key not provided and JINA_API_KEY env variable not set")

        self.model = model or os.getenv("JINA_EMBED_MODEL", "jina-embeddings-v3")
        self.api_url = "https://api.jina.ai/v1/embeddings"
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            Exception: If embedding generation fails after retries
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text")
        
        for attempt in range(self.max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,
                    "input": [text]
                }
                
                response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Extract embedding vector
                return response.json()["data"][0]["embedding"]
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"Embedding generation attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    raise Exception(f"Failed to generate embedding after {self.max_retries} attempts: {e}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Jina API supports batch requests which is more efficient than
        generating embeddings one by one.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors (one per input text)
            
        Raises:
            Exception: If batch embedding generation fails after retries
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("No valid texts to embed")
        
        for attempt in range(self.max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,
                    "input": valid_texts
                }
                
                response = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
                response.raise_for_status()
                
                # Extract embeddings in order
                embeddings = [item["embedding"] for item in response.json()["data"]]
                return embeddings
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"Batch embedding attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise Exception(f"Failed to generate batch embeddings after {self.max_retries} attempts: {e}")
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.
        
        Returns:
            Dimension of embedding vectors
        """
        model_dimensions = {
            "jina-embeddings-v3": 1024,
            "jina-embeddings-v2-base-en": 768,
            "jina-embeddings-v2-base-es": 768,
        }
        if self.model in model_dimensions:
            return model_dimensions[self.model]

        # Default for unknown models
        return int(os.getenv("JINA_EMBED_DIM", "1024"))
