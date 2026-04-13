"""
Ingestion service
Orchestrates the full document processing pipeline with error handling and retry mechanisms
"""

import logging
import uuid
from typing import List, Dict, Optional
from datetime import datetime

from ..utils.pdf_loader import extract_text_from_pdf
from ..utils.chunker import chunk_text_by_tokens
from .embedding_service import EmbeddingService
from .vector_store import VectorStore

logger = logging.getLogger(__name__)

class IngestionService:
    """Service for orchestrating the document ingestion pipeline with error handling"""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[VectorStore] = None
    ):
        """
        Initialize the ingestion service

        Args:
            embedding_service (Optional[EmbeddingService]): Embedding service instance
            vector_store (Optional[VectorStore]): Vector store instance
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()

    def ingest_document(
        self,
        file_path: str,
        document_id: Optional[str] = None,
        chunk_size: int = 512,
        overlap: int = 50
    ) -> Dict:
        """
        Ingest a document through the full pipeline:
        1. Load document
        2. Extract text
        3. Chunk text
        4. Generate embeddings
        5. Store in vector database

        Args:
            file_path (str): Path to the document file
            document_id (Optional[str]): Document ID (generated if not provided)
            chunk_size (int): Size of chunks in tokens
            overlap (int): Overlap between chunks in tokens

        Returns:
            Dict: Ingestion result with status and document info
        """
        try:
            # Generate document ID if not provided
            if document_id is None:
                document_id = str(uuid.uuid4())

            logger.info(f"Ingesting document {file_path} with ID {document_id}")

            # Step 1: Load and extract text
            logger.info("Step 1: Extracting text from document")
            text = extract_text_from_pdf(file_path)

            logger.debug(f"TEXT LENGTH: {len(text)}")
            if len(text) > 0:
                logger.debug(f"TEXT SAMPLE: {text[:200]}")

            if not text.strip():
                raise ValueError("Document text is empty")

            # Step 2: Chunk text
            logger.info("Step 2: Chunking text")
            chunks = chunk_text_by_tokens(
                text=text,
                chunk_size=chunk_size,
                overlap=overlap
            )

            if not chunks:
                raise ValueError("No chunks generated from document")

            logger.info(f"Generated {len(chunks)} chunks")

            # Step 3: Generate embeddings
            logger.info("Step 3: Generating embeddings")
            embeddings = self.embedding_service.embed_texts(chunks)

            # Step 4: Prepare metadata for each chunk
            metadatas = []
            chunk_ids = []

            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{i}"
                metadata = {
                    "document_id": document_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_path": file_path,
                    "ingested_at": datetime.now().isoformat(),
                }
                metadatas.append(metadata)
                chunk_ids.append(chunk_id)

            # Step 5: Store in vector database
            logger.info("Step 4: Storing embeddings in vector database")
            self.vector_store.add_documents(
                documents=chunks,
                embeddings=embeddings,
                ids=chunk_ids,
                metadatas=metadatas
            )

            result = {
                "document_id": document_id,
                "file_path": file_path,
                "chunks_processed": len(chunks),
                "status": "success",
                "message": "Document ingested successfully"
            }

            logger.info(f"Document ingestion completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error ingesting document {file_path}: {str(e)}")
            return {
                "document_id": document_id or "unknown",
                "file_path": file_path,
                "chunks_processed": 0,
                "status": "error",
                "message": f"Error ingesting document: {str(e)}"
            }

    def delete_document(self, document_id: str) -> Dict:
        """
        Delete a document and all its chunks from the vector store

        Args:
            document_id (str): ID of the document to delete

        Returns:
            Dict: Deletion result
        """
        try:
            logger.info(f"Deleting document with ID: {document_id}")

            # Query for all chunks with the document_id
            logger.info("Querying for document chunks")
            query_result = self.vector_store.query(
                query_embeddings=[[0.0] * self.embedding_service.get_embedding_dimension()],  # Dummy query
                n_results=100,  # Adjust based on expected max chunks per document
                where={"document_id": document_id}
            )

            # Extract chunk IDs to delete
            if query_result and 'ids' in query_result and query_result['ids']:
                chunk_ids = query_result['ids'][0]  # ChromaDB returns list of lists
                if chunk_ids:
                    logger.info(f"Found {len(chunk_ids)} chunks to delete")

                    # Delete all chunks
                    self.vector_store.delete_documents(chunk_ids)

                    result = {
                        "document_id": document_id,
                        "status": "success",
                        "message": f"Document deleted successfully. Removed {len(chunk_ids)} chunks."
                    }
                else:
                    result = {
                        "document_id": document_id,
                        "status": "warning",
                        "message": "No chunks found for document ID"
                    }
            else:
                result = {
                    "document_id": document_id,
                    "status": "warning",
                    "message": "No chunks found for document ID"
                }

            logger.info(f"Document deletion completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return {
                "document_id": document_id,
                "status": "error",
                "message": f"Error deleting document: {str(e)}"
            }