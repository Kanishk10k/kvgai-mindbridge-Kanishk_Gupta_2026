"""
Vector store service
Handles ChromaDB operations for storing and retrieving embeddings
"""

import logging
from typing import List, Dict, Optional, Union
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class VectorStore:
    """Service for interacting with ChromaDB vector store"""

    def __init__(self, collection_name: str = "documents", persist_directory: str = "./chroma_db"):
        """
        Initialize the vector store

        Args:
            collection_name (str): Name of the ChromaDB collection
            persist_directory (str): Directory to persist the database
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize ChromaDB client and collection"""
        try:
            logger.info("Initializing ChromaDB client")
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
            logger.info(f"ChromaDB collection '{self.collection_name}' initialized")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {str(e)}")
            raise

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> None:
        """
        Add documents with their embeddings to the vector store

        Args:
            documents (List[str]): List of document texts
            embeddings (List[List[float]]): List of embedding vectors
            ids (List[str]): List of document IDs
            metadatas (Optional[List[Dict]]): List of metadata dictionaries
        """
        try:
            logger.info(f"Adding {len(documents)} documents to vector store")
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )
            logger.info("Documents added successfully")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Query the vector store for similar documents

        Args:
            query_embeddings (List[List[float]]): List of query embedding vectors
            n_results (int): Number of results to return
            where (Optional[Dict]): Metadata filters

        Returns:
            Dict: Query results
        """
        try:
            logger.info(f"Querying vector store for {len(query_embeddings)} embeddings")
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where
            )
            logger.info("Query completed successfully")
            return results
        except Exception as e:
            logger.error(f"Error querying vector store: {str(e)}")
            raise

    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by IDs

        Args:
            ids (List[str]): List of document IDs to delete
        """
        try:
            logger.info(f"Deleting {len(ids)} documents from vector store")
            self.collection.delete(ids=ids)
            logger.info("Documents deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise

    def get_document_count(self) -> int:
        """
        Get the total number of documents in the collection

        Returns:
            int: Number of documents
        """
        try:
            count = self.collection.count()
            logger.info(f"Collection contains {count} documents")
            return count
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            raise

    def reset_collection(self) -> None:
        """
        Reset (delete all documents from) the collection
        """
        try:
            logger.info(f"Resetting collection '{self.collection_name}'")
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
            logger.info("Collection reset successfully")
        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}")
            raise