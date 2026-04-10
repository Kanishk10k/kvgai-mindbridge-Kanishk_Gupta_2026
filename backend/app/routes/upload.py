from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import logging
import os
from pathlib import Path

# Import the ingestion service
from ..services.ingestion_service import IngestionService

router = APIRouter()

logger = logging.getLogger(__name__)

# Define the directory for saving uploaded files
UPLOAD_DIR = Path("./data/raw")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def is_valid_pdf(filename: str) -> bool:
    """
    Validate if the file is a PDF

    Args:
        filename (str): Name of the file to validate

    Returns:
        bool: True if file is a PDF, False otherwise
    """
    return filename.lower().endswith('.pdf')

def save_upload_file(file: UploadFile, destination: Path) -> Path:
    """
    Save an uploaded file to a destination path

    Args:
        file (UploadFile): The uploaded file
        destination (Path): Destination path to save the file

    Returns:
        Path: Path to the saved file
    """
    try:
        with destination.open("wb") as buffer:
            file.file.seek(0)  # Reset file pointer to beginning
            while chunk := file.file.read(8192):
                buffer.write(chunk)
        logger.info(f"File saved to {destination}")
        return destination
    except Exception as e:
        logger.error(f"Error saving file {file.filename}: {str(e)}")
        raise

@router.post("/")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for processing

    Args:
        file (UploadFile): The document file to upload

    Returns:
        dict: Result of the ingestion process
    """
    try:
        logger.info(f"Uploading file: {file.filename}")

        # Validate file type
        if not is_valid_pdf(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF files are allowed."
            )

        # Save file to local directory
        file_path = UPLOAD_DIR / file.filename
        logger.info(f"Saving file to: {file_path}")

        # Save the file
        saved_file_path = save_upload_file(file, file_path)

        # Initialize ingestion service
        ingestion_service = IngestionService()

        # Process the saved file
        logger.info(f"Processing file: {saved_file_path}")
        ingestion_result = ingestion_service.ingest_document(str(saved_file_path))

        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "document_id": ingestion_result["document_id"],
            "chunks_processed": ingestion_result["chunks_processed"],
            "status": ingestion_result["status"],
            "message": ingestion_result["message"]
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )

@router.delete("/{file_id}")
async def delete_document(file_id: str):
    """
    Delete a document by ID

    Args:
        file_id (str): The ID of the document to delete

    Returns:
        dict: Status of the deletion operation
    """
    try:
        logger.info(f"Deleting document with ID: {file_id}")

        # Initialize ingestion service
        ingestion_service = IngestionService()

        # Delete the document
        deletion_result = ingestion_service.delete_document(file_id)

        return {
            "file_id": file_id,
            "status": deletion_result["status"],
            "message": deletion_result["message"]
        }
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )