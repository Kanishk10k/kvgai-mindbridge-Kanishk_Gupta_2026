"""
Initialization module for core services
"""

import logging
from typing import Tuple

from .config import Config
from ..services.embedding_service import EmbeddingService
from ..services.vector_store import VectorStore

logger = logging.getLogger(__name__)

def initialize_core_services() -> Tuple[EmbeddingService, VectorStore]:
    """
    Initialize core services: embedding service and vector store

    Returns:
        Tuple[EmbeddingService, VectorStore]: Initialized services
    """
    try:
        logger.info("Initializing core services")

        # Initialize embedding service
        embedding_config = Config.get_embedding_config()
        logger.info(f"Initializing embedding service with config: {embedding_config}")
        embedding_service = EmbeddingService(**embedding_config)

        # Initialize vector store
        vector_store_config = Config.get_vector_store_config()
        logger.info(f"Initializing vector store with config: {vector_store_config}")
        vector_store = VectorStore(**vector_store_config)

        logger.info("Core services initialized successfully")
        return embedding_service, vector_store

    except Exception as e:
        logger.error(f"Error initializing core services: {str(e)}")
        raise

def initialize_embedding_service() -> EmbeddingService:
    """
    Initialize only the embedding service

    Returns:
        EmbeddingService: Initialized embedding service
    """
    try:
        logger.info("Initializing embedding service")
        embedding_config = Config.get_embedding_config()
        embedding_service = EmbeddingService(**embedding_config)
        logger.info("Embedding service initialized successfully")
        return embedding_service
    except Exception as e:
        logger.error(f"Error initializing embedding service: {str(e)}")
        raise

def initialize_vector_store() -> VectorStore:
    """
    Initialize only the vector store

    Returns:
        VectorStore: Initialized vector store
    """
    try:
        logger.info("Initializing vector store")
        vector_store_config = Config.get_vector_store_config()
        vector_store = VectorStore(**vector_store_config)
        logger.info("Vector store initialized successfully")
        return vector_store
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        raise