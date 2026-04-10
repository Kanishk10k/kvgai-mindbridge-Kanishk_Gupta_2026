"""
Configuration module for core services
"""

import os
from typing import Optional

class Config:
    """Configuration class for core services"""

    # Vector store configuration
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "documents")

    # Embedding model configuration
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

    # Chunking configuration
    DEFAULT_CHUNK_SIZE: int = int(os.getenv("DEFAULT_CHUNK_SIZE", "512"))
    DEFAULT_OVERLAP: int = int(os.getenv("DEFAULT_OVERLAP", "50"))

    # API configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    @classmethod
    def get_vector_store_config(cls) -> dict:
        """Get vector store configuration"""
        return {
            "persist_directory": cls.CHROMA_PERSIST_DIRECTORY,
            "collection_name": cls.CHROMA_COLLECTION_NAME
        }

    @classmethod
    def get_embedding_config(cls) -> dict:
        """Get embedding model configuration"""
        return {
            "model_name": cls.EMBEDDING_MODEL_NAME
        }

    @classmethod
    def get_chunking_config(cls) -> dict:
        """Get chunking configuration"""
        return {
            "chunk_size": cls.DEFAULT_CHUNK_SIZE,
            "overlap": cls.DEFAULT_OVERLAP
        }