"""
Vector store service
Handles ChromaDB operations for storing and retrieving embeddings with retry mechanisms
"""

import logging
import time
from typing import List, Dict, Optional, Union
import chromadb
from chromadb.config import Settings
from ..core.config import Config

logger = logging.getLogger(__name__)

class VectorStore:
    """Service for interacting with ChromaDB vector store with retry mechanisms"""

    def __init__(self, collection_name: str = None, persist_directory: str = None):
        """
        Initialize the vector store

        Args:
            collection_name (str): Name of the ChromaDB collection
            persist_directory (str): Directory to persist the database
        """
        self.collection_name = collection_name or Config.CHROMA_COLLECTION_NAME
        self.persist_directory = persist_directory or Config.CHROMA_PERSIST_DIRECTORY
        self.client = None
        self.collection = None
        self.max_retries = Config.CHROMADB_MAX_RETRIES
        self.retry_delay = Config.RETRY_DELAY_SECONDS
        self.timeout = Config.CHROMADB_TIMEOUT
        self._initialize_client()

    def _initialize_client(self):
        """Initialize ChromaDB client and collection with retries"""
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Initializing ChromaDB client (attempt {attempt + 1})")
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(anonymized_telemetry=False)
                )

                # Get or create collection
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name
                )
                logger.info(f"ChromaDB collection '{self.collection_name}' initialized")
                return
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Failed to initialize ChromaDB client (attempt {attempt + 1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Error initializing ChromaDB client after {self.max_retries + 1} attempts: {str(e)}")
                    raise

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> None:
        """
        Add documents with their embeddings to the vector store with retry mechanism

        Args:
            documents (List[str]): List of document texts
            embeddings (List[List[float]]): List of embedding vectors
            ids (List[str]): List of document IDs
            metadatas (Optional[List[Dict]]): List of metadata dictionaries
        """
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Adding {len(documents)} documents to vector store (attempt {attempt + 1})")
                self.collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    ids=ids,
                    metadatas=metadatas
                )
                logger.info("Documents added successfully")
                return
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Failed to add documents to vector store (attempt {attempt + 1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Error adding documents to vector store after {self.max_retries + 1} attempts: {str(e)}")
                    raise

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Query the vector store for similar documents with retry mechanism

        Args:
            query_embeddings (List[List[float]]): List of query embedding vectors
            n_results (int): Number of results to return
            where (Optional[Dict]): Metadata filters

        Returns:
            Dict: Query results
        """
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Querying vector store for {len(query_embeddings)} embeddings (attempt {attempt + 1})")
                results = self.collection.query(
                    query_embeddings=query_embeddings,
                    n_results=n_results,
                    where=where
                )
                logger.info("Query completed successfully")
                return results
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Failed to query vector store (attempt {attempt + 1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Error querying vector store after {self.max_retries + 1} attempts: {str(e)}")
                    raise

    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by IDs with retry mechanism

        Args:
            ids (List[str]): List of document IDs to delete
        """
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Deleting {len(ids)} documents from vector store (attempt {attempt + 1})")
                self.collection.delete(ids=ids)
                logger.info("Documents deleted successfully")
                return
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Failed to delete documents (attempt {attempt + 1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Error deleting documents after {self.max_retries + 1} attempts: {str(e)}")
                    raise

    def get_document_count(self) -> int:
        """
        Get the total number of documents in the collection with retry mechanism

        Returns:
            int: Number of documents
        """
        for attempt in range(self.max_retries + 1):
            try:
                count = self.collection.count()
                logger.info(f"Collection contains {count} documents")
                return count
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Failed to get document count (attempt {attempt + 1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Error getting document count after {self.max_retries + 1} attempts: {str(e)}")
                    raise

    def reset_collection(self) -> None:
        """
        Reset (delete all documents from) the collection with retry mechanism
        """
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Resetting collection '{self.collection_name}' (attempt {attempt + 1})")
                self.client.delete_collection(name=self.collection_name)
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name
                )
                logger.info("Collection reset successfully")
                return
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Failed to reset collection (attempt {attempt + 1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Error resetting collection after {self.max_retries + 1} attempts: {str(e)}")
                    raise