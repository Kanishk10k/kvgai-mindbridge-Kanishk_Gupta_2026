"""
Embedding service
Handles text embedding generation using various models with retry mechanisms
"""

import logging
import time
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from ..core.config import Config

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating text embeddings with retry mechanisms"""

    def __init__(self, model_name: str = None):
        """
        Initialize the embedding service

        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        self.model_name = model_name or Config.EMBEDDING_MODEL_NAME
        self.model = None
        self.max_retries = Config.OLLAMA_MAX_RETRIES
        self.retry_delay = Config.RETRY_DELAY_SECONDS
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the sentence transformer model with retries"""
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Loading embedding model: {self.model_name} (attempt {attempt + 1})")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully")
                return
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Failed to load embedding model {self.model_name} (attempt {attempt + 1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Error loading embedding model {self.model_name} after {self.max_retries + 1} attempts: {str(e)}")
                    raise

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text with retry mechanism

        Args:
            text (str): Text to embed

        Returns:
            List[float]: Embedding vector
        """
        if not self.model:
            raise RuntimeError("Embedding model not initialized")

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Generating embedding for text: {text[:50]}...")
                embedding = self.model.encode(text).tolist()
                return embedding
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Failed to generate embedding (attempt {attempt + 1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Error generating embedding after {self.max_retries + 1} attempts: {str(e)}")
                    raise

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with retry mechanism

        Args:
            texts (List[str]): List of texts to embed

        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not self.model:
            raise RuntimeError("Embedding model not initialized")

        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Generating embeddings for {len(texts)} texts (attempt {attempt + 1})")
                embeddings = self.model.encode(texts).tolist()
                return embeddings
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Failed to generate embeddings (attempt {attempt + 1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Error generating embeddings after {self.max_retries + 1} attempts: {str(e)}")
                    raise

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors with error handling

        Returns:
            int: Dimension of embedding vectors
        """
        if not self.model:
            raise RuntimeError("Embedding model not initialized")

        for attempt in range(self.max_retries + 1):
            try:
                # Generate a sample embedding to determine dimension
                sample_embedding = self.embed_text("sample text")
                return len(sample_embedding)
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Failed to get embedding dimension (attempt {attempt + 1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Error getting embedding dimension after {self.max_retries + 1} attempts: {str(e)}")
                    raise