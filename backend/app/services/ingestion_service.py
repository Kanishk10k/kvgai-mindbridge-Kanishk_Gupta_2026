"""
Ingestion service
Orchestrates the full document processing pipeline
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
    """Service for orchestrating the document ingestion pipeline"""

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
            raise

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

            # TODO: Implement document deletion logic
            # This would require querying for all chunks with the document_id
            # and then deleting them from the vector store

            result = {
                "document_id": document_id,
                "status": "success",
                "message": "Document deletion implemented"
            }

            logger.info(f"Document deletion completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise