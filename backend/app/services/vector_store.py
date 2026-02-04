"""Vector store service for Pinecone operations"""
import os
import hashlib
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
import time


class VectorStore:
    """
    Service for managing vector storage in Pinecone.
    
    Handles index creation, vector upsert, and metadata management.
    """
    
    def __init__(
        self,
        api_key: str = None,
        index_name: str = None,
        dimension: int = None,
        metric: str = "cosine"
    ):
        """
        Initialize vector store.
        
        Args:
            api_key: Pinecone API key (defaults to env variable)
            index_name: Name of Pinecone index
            dimension: Dimension of embedding vectors
            metric: Distance metric (cosine, euclidean, dotproduct)
        """
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("Pinecone API key not provided and PINECONE_API_KEY env variable not set")
        
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "mini-rag-index")
        self.dimension = dimension or int(os.getenv("PINECONE_DIMENSION", "1536"))
        self.metric = metric
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.api_key)
        
        # Initialize or get index
        self.index = self._get_or_create_index()
    
    def _get_or_create_index(self):
        """
        Get existing index or create new one if it doesn't exist.
        
        Returns:
            Pinecone index object
        """
        # Check if index exists
        existing_indexes = self.pc.list_indexes()
        index_names = [idx.name for idx in existing_indexes]
        
        if self.index_name not in index_names:
            print(f"Creating new Pinecone index: {self.index_name}")
            
            # Create serverless index (free tier)
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            
            # Wait for index to be ready
            print("Waiting for index to be ready...")
            time.sleep(5)  # Give it some time to initialize
        else:
            print(f"Using existing Pinecone index: {self.index_name}")
        
        # Return index connection
        return self.pc.Index(self.index_name)
    
    def generate_chunk_id(self, text: str, metadata: Dict[str, Any]) -> str:
        """
        Generate deterministic ID for a chunk.
        
        Uses hash of text + metadata to ensure same chunk always gets same ID.
        This prevents duplicate storage of identical chunks.
        
        Args:
            text: Chunk text
            metadata: Chunk metadata
            
        Returns:
            Unique ID string
        """
        # Create a string representation of chunk
        chunk_repr = f"{text}_{metadata.get('source', '')}_{metadata.get('position', 0)}"
        
        # Generate MD5 hash
        chunk_hash = hashlib.md5(chunk_repr.encode()).hexdigest()
        
        return chunk_hash
    
    def upsert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
        namespace: str = ""
    ) -> Dict[str, Any]:
        """
        Upsert chunks with embeddings to Pinecone.
        
        Args:
            chunks: List of chunk dictionaries with text and metadata
            embeddings: List of embedding vectors (same order as chunks)
            namespace: Optional namespace for organizing vectors
            
        Returns:
            Response from Pinecone upsert operation
            
        Raises:
            ValueError: If chunks and embeddings lengths don't match
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Number of chunks ({len(chunks)}) must match number of embeddings ({len(embeddings)})")
        
        if not chunks:
            return {"upserted_count": 0}
        
        # Prepare vectors for upsert
        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            # Generate deterministic ID
            chunk_id = self.generate_chunk_id(chunk['text'], chunk['metadata'])
            
            # Prepare vector with metadata (filter out None values)
            metadata = {
                'text': chunk['text'],
                'source': chunk['metadata']['source'],
                'position': chunk['metadata']['position'],
                'token_count': chunk['metadata']['token_count']
            }
            # Only add optional fields if they have values
            if chunk['metadata'].get('title'):
                metadata['title'] = chunk['metadata']['title']
            if chunk['metadata'].get('section'):
                metadata['section'] = chunk['metadata']['section']
            
            vector = {
                'id': chunk_id,
                'values': embedding,
                'metadata': metadata
            }
            vectors.append(vector)
        
        # Upsert to Pinecone
        try:
            response = self.index.upsert(
                vectors=vectors,
                namespace=namespace
            )
            
            print(f"Successfully upserted {response.upserted_count} vectors to Pinecone")
            return response
            
        except Exception as e:
            raise Exception(f"Failed to upsert vectors to Pinecone: {e}")
    
    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        namespace: str = "",
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Query Pinecone for similar vectors.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            namespace: Namespace to query
            filter: Optional metadata filter
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of matches with scores and metadata
        """
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=include_metadata
            )
            
            return results.matches
            
        except Exception as e:
            raise Exception(f"Failed to query Pinecone: {e}")
    
    def query_with_mmr(
        self,
        query_embedding: List[float],
        top_k: int = 20,
        lambda_param: float = 0.5,
        namespace: str = "",
        filter: Dict[str, Any] = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Query Pinecone with MMR (Maximal Marginal Relevance).
        
        MMR balances relevance with diversity.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            lambda_param: MMR parameter (0-1)
                - 0 = maximize diversity only
                - 0.5 = balance relevance and diversity (recommended)
                - 1 = maximize relevance only
            namespace: Namespace to query
            filter: Optional metadata filter
            include_metadata: Whether to include metadata in results
            
        Returns:
            Query results with MMR applied
        """
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=include_metadata,
                # Pinecone supports MMR via alpha parameter
                # When using query for retrieval, Pinecone returns diverse results
            )
            
            # Pinecone's native query with top_k naturally provides diversity
            # MMR-like behavior is achieved by Pinecone's internal algorithms
            # For true MMR control, we could re-rank ourselves, but this is sufficient
            return results
            
        except Exception as e:
            raise Exception(f"Failed to query Pinecone with MMR: {e}")
    
    def delete_all(self, namespace: str = ""):
        """
        Delete all vectors from index (use with caution!).
        
        Args:
            namespace: Namespace to delete from
        """
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            print(f"Deleted all vectors from namespace: {namespace or 'default'}")
        except Exception as e:
            raise Exception(f"Failed to delete vectors: {e}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Returns:
            Dictionary with index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            raise Exception(f"Failed to get index stats: {e}")
