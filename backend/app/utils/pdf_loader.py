"""
PDF loading utility
Handles PDF text extraction operations with error handling
"""

import logging
from typing import List
from pypdf import PdfReader
import os

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file with comprehensive error handling

    Args:
        file_path (str): Path to the PDF file

    Returns:
        str: Extracted text or empty string if error occurs
    """
    try:
        logger.info(f"Extracting text from PDF: {file_path}")

        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"PDF file not found: {file_path}")
            return ""

        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            logger.error(f"PDF file not readable: {file_path}")
            return ""

        reader = PdfReader(file_path)
        text = ""

        # Log PDF info
        logger.info(f"PDF has {len(reader.pages)} pages")

        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    logger.debug(f"Extracted text from page {page_num + 1}, length: {len(page_text)}")
                else:
                    logger.warning(f"No text found on page {page_num + 1}")
            except Exception as page_error:
                logger.warning(f"Error extracting text from page {page_num + 1}: {str(page_error)}")
                continue

        text = text.strip()

        logger.info(f"Successfully extracted text from PDF. Total length: {len(text)}")
        return text

    except FileNotFoundError:
        logger.error(f"PDF file not found: {file_path}")
        return ""
    except PermissionError:
        logger.error(f"Permission denied accessing PDF file: {file_path}")
        return ""
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
        return ""

def get_pdf_metadata(file_path: str) -> dict:
    """
    Extract metadata from a PDF file with error handling

    Args:
        file_path (str): Path to the PDF file

    Returns:
        dict: Metadata extracted from the PDF
    """
    try:
        logger.info(f"Extracting metadata from PDF: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"PDF file not found for metadata extraction: {file_path}")
            return {
                "title": "Unknown",
                "author": "Unknown",
                "pages": 0,
                "error": "File not found"
            }

        reader = PdfReader(file_path)

        # Get basic metadata
        metadata = reader.metadata

        result = {
            "title": getattr(metadata, 'title', 'Unknown') if metadata else 'Unknown',
            "author": getattr(metadata, 'author', 'Unknown') if metadata else 'Unknown',
            "pages": len(reader.pages)
        }

        logger.info(f"Successfully extracted metadata: {result}")
        return result

    except Exception as e:
        logger.error(f"Error extracting metadata from PDF {file_path}: {str(e)}")
        return {
            "title": "Unknown",
            "author": "Unknown",
            "pages": 0,
            "error": str(e)
        }