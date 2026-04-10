"""
Embedding service
Handles text embedding generation using various models
"""

import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating text embeddings"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding service

        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the sentence transformer model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model {self.model_name}: {str(e)}")
            raise

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text (str): Text to embed

        Returns:
            List[float]: Embedding vector
        """
        if not self.model:
            raise RuntimeError("Embedding model not initialized")

        try:
            logger.debug(f"Generating embedding for text: {text[:50]}...")
            embedding = self.model.encode(text).tolist()
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts (List[str]): List of texts to embed

        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not self.model:
            raise RuntimeError("Embedding model not initialized")

        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.model.encode(texts).tolist()
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors

        Returns:
            int: Dimension of embedding vectors
        """
        if not self.model:
            raise RuntimeError("Embedding model not initialized")

        # Generate a sample embedding to determine dimension
        sample_embedding = self.embed_text("sample text")
        return len(sample_embedding)