from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import logging
import os
import mimetypes
from pathlib import Path

# Import the ingestion service
from ..services.ingestion_service import IngestionService
from ..core.config import Config

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

def is_valid_file_type(file: UploadFile) -> bool:
    """
    Validate file type using MIME type detection

    Args:
        file (UploadFile): The uploaded file

    Returns:
        bool: True if file type is valid, False otherwise
    """
    # Check file extension
    if not is_valid_pdf(file.filename):
        return False

    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type and not mime_type.startswith('application/pdf'):
        return False

    return True

def is_file_size_valid(file: UploadFile) -> bool:
    """
    Validate file size

    Args:
        file (UploadFile): The uploaded file

    Returns:
        bool: True if file size is valid, False otherwise
    """
    # Note: We can't easily check file size without reading the entire file
    # This is a placeholder for future implementation
    return True

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks

    Args:
        filename (str): Original filename

    Returns:
        str: Sanitized filename
    """
    # Remove any path components and keep only the filename
    sanitized = os.path.basename(filename)
    # Remove any suspicious characters
    sanitized = "".join(c for c in sanitized if c.isalnum() or c in "._- ")
    return sanitized

def save_upload_file(file: UploadFile, destination: Path) -> Path:
    """
    Save an uploaded file to a destination path with validation

    Args:
        file (UploadFile): The uploaded file
        destination (Path): Destination path to save the file

    Returns:
        Path: Path to the saved file
    """
    try:
        # Additional security: ensure destination is within UPLOAD_DIR
        if not str(destination.resolve()).startswith(str(UPLOAD_DIR.resolve())):
            raise ValueError("Invalid file path")

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
    Upload a document for processing with enhanced validation

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

        # Additional MIME type validation
        if not is_valid_file_type(file):
            raise HTTPException(
                status_code=400,
                detail="Invalid file content. File is not a valid PDF."
            )

        # Validate file size
        if file.size and file.size > Config.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {Config.MAX_FILE_SIZE_MB}MB."
            )

        # Sanitize filename to prevent path traversal
        sanitized_filename = sanitize_filename(file.filename)
        if not sanitized_filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename."
            )

        # Save file to local directory with sanitized name
        file_path = UPLOAD_DIR / sanitized_filename
        logger.info(f"Saving file to: {file_path}")

        # Save the file
        saved_file_path = save_upload_file(file, file_path)

        # Initialize ingestion service
        ingestion_service = IngestionService()

        # Process the saved file
        logger.info(f"Processing file: {saved_file_path}")
        ingestion_result = ingestion_service.ingest_document(str(saved_file_path))

        # Clean up temporary file if ingestion failed
        if ingestion_result["status"] == "error" and saved_file_path.exists():
            try:
                saved_file_path.unlink()
                logger.info(f"Cleaned up temporary file: {saved_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {saved_file_path}: {str(e)}")

        return {
            "filename": sanitized_filename,
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