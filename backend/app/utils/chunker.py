"""
Text chunking utility
Handles text segmentation based on tokens for LLM processing

Token-based chunking is preferred over character-based chunking because:
1. LLMs process text as tokens, so token-based chunking ensures consistent context window utilization
2. Different languages and character sets have varying tokenization ratios
3. Token-based chunking provides more predictable model behavior and performance
4. It aligns with how the model actually processes text internally
"""

import logging
from typing import List
import tiktoken

logger = logging.getLogger(__name__)

def get_tokenizer(encoding_name: str = "cl100k_base"):
    """
    Get a tokenizer by name

    Args:
        encoding_name (str): Name of the encoding to use

    Returns:
        tiktoken.Encoding: Tokenizer instance
    """
    try:
        tokenizer = tiktoken.get_encoding(encoding_name)
        return tokenizer
    except Exception as e:
        logger.error(f"Error initializing tokenizer {encoding_name}: {str(e)}")
        # Fallback to default encoding
        return tiktoken.get_encoding("cl100k_base")

def chunk_text_by_tokens(
    text: str,
    chunk_size: int = 512,
    overlap: int = 50,
    encoding_name: str = "cl100k_base"
) -> List[str]:
    """
    Split text into chunks based on token count with overlap

    Args:
        text (str): Text to chunk
        chunk_size (int): Size of each chunk in tokens
        overlap (int): Overlap between chunks in tokens
        encoding_name (str): Name of the encoding for tokenization

    Returns:
        List[str]: List of text chunks
    """
    # Initialize tokenizer
    tokenizer = get_tokenizer(encoding_name)

    # Encode text to tokens
    tokens = tokenizer.encode(text)
    logger.info(f"Total tokens: {len(tokens)}")

    # Create chunks of tokens
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        # Get token slice
        token_chunk = tokens[i:i + chunk_size]
        # Decode tokens back to text
        text_chunk = tokenizer.decode(token_chunk)
        chunks.append(text_chunk)

        # Stop if we've reached the end
        if i + chunk_size >= len(tokens):
            break

    logger.info(f"Created {len(chunks)} token-based chunks")
    return chunks

def chunk_by_sentences_with_token_limit(
    text: str,
    max_tokens: int = 512,
    encoding_name: str = "cl100k_base"
) -> List[str]:
    """
    Split text into sentence-aware chunks respecting token limits

    Args:
        text (str): Text to chunk
        max_tokens (int): Maximum tokens per chunk
        encoding_name (str): Name of the encoding for tokenization

    Returns:
        List[str]: List of sentence-aware text chunks
    """
    # Initialize tokenizer
    tokenizer = get_tokenizer(encoding_name)

    # Split text into sentences (simple split by periods)
    sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # Check if adding this sentence would exceed token limit
        test_chunk = current_chunk + " " + sentence if current_chunk else sentence
        token_count = len(tokenizer.encode(test_chunk))

        if token_count <= max_tokens:
            current_chunk = test_chunk
        else:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    # Add remaining text as final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    logger.info(f"Created {len(chunks)} sentence-aware chunks")
    return chunks