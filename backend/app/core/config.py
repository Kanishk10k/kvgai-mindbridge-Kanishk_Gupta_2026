"""
Configuration module for core services
"""

import os
import requests
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

    # Ollama configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    # Timeout configuration (in seconds)
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "300"))
    CHROMADB_TIMEOUT: int = int(os.getenv("CHROMADB_TIMEOUT", "30"))
    FILE_UPLOAD_TIMEOUT: int = int(os.getenv("FILE_UPLOAD_TIMEOUT", "300"))

    # Retry configuration
    OLLAMA_MAX_RETRIES: int = int(os.getenv("OLLAMA_MAX_RETRIES", "2"))
    CHROMADB_MAX_RETRIES: int = int(os.getenv("CHROMADB_MAX_RETRIES", "3"))
    RETRY_DELAY_SECONDS: float = float(os.getenv("RETRY_DELAY_SECONDS", "5.0"))

    # File upload configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))

    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate critical configuration values

        Returns:
            bool: True if all validations pass, False otherwise
        """
        try:
            # Validate ChromaDB persistence directory
            if not cls.validate_chroma_persist_directory():
                return False

            # Validate Ollama service connectivity
            if not cls.validate_ollama_connectivity():
                return False

            return True
        except Exception as e:
            print(f"Configuration validation error: {str(e)}")
            return False

    @classmethod
    def validate_chroma_persist_directory(cls) -> bool:
        """
        Validate that the ChromaDB persistence directory exists and is writable

        Returns:
            bool: True if directory is valid, False otherwise
        """
        try:
            persist_dir = cls.CHROMA_PERSIST_DIRECTORY
            if not os.path.exists(persist_dir):
                # Try to create the directory
                os.makedirs(persist_dir, exist_ok=True)
                print(f"Created ChromaDB persistence directory: {persist_dir}")

            # Check if directory is writable
            if not os.access(persist_dir, os.W_OK):
                print(f"ChromaDB persistence directory is not writable: {persist_dir}")
                return False

            return True
        except Exception as e:
            print(f"Error validating ChromaDB persistence directory: {str(e)}")
            return False

    @classmethod
    def validate_ollama_connectivity(cls) -> bool:
        """
        Validate that the Ollama service is reachable

        Returns:
            bool: True if Ollama is reachable, False otherwise
        """
        try:
            ollama_url = f"{cls.OLLAMA_HOST}/api/tags"
            response = requests.get(ollama_url, timeout=5)
            if response.status_code == 200:
                return True
            else:
                print(f"Ollama service returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error connecting to Ollama service: {str(e)}")
            return False

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

    @classmethod
    def get_ollama_config(cls) -> dict:
        """Get Ollama configuration"""
        return {
            "host": cls.OLLAMA_HOST,
            "model": cls.OLLAMA_MODEL,
            "timeout": cls.OLLAMA_TIMEOUT,
            "max_retries": cls.OLLAMA_MAX_RETRIES
        }