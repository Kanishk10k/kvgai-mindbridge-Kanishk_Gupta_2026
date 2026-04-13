"""
Text chunking utility
Handles text segmentation based on tokens for LLM processing with enhanced logging

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
    Get a tokenizer by name with error handling

    Args:
        encoding_name (str): Name of the encoding to use

    Returns:
        tiktoken.Encoding: Tokenizer instance
    """
    try:
        logger.debug(f"Initializing tokenizer: {encoding_name}")
        tokenizer = tiktoken.get_encoding(encoding_name)
        logger.debug(f"Tokenizer {encoding_name} initialized successfully")
        return tokenizer
    except Exception as e:
        logger.error(f"Error initializing tokenizer {encoding_name}: {str(e)}")
        # Fallback to default encoding
        fallback_tokenizer = tiktoken.get_encoding("cl100k_base")
        logger.info("Using fallback tokenizer cl100k_base")
        return fallback_tokenizer

def chunk_text_by_tokens(
    text: str,
    chunk_size: int = 512,
    overlap: int = 50,
    encoding_name: str = "cl100k_base"
) -> List[str]:
    """
    Split text into chunks based on token count with overlap and enhanced logging

    Args:
        text (str): Text to chunk
        chunk_size (int): Size of each chunk in tokens
        overlap (int): Overlap between chunks in tokens
        encoding_name (str): Name of the encoding for tokenization

    Returns:
        List[str]: List of text chunks
    """
    logger.info(f"Chunking text with chunk_size={chunk_size}, overlap={overlap}, encoding={encoding_name}")

    # Initialize tokenizer
    tokenizer = get_tokenizer(encoding_name)

    # Encode text to tokens
    tokens = tokenizer.encode(text)
    logger.info(f"Total tokens in text: {len(tokens)}")

    # Handle edge case of empty text
    if len(tokens) == 0:
        logger.warning("Empty text provided for chunking")
        return []

    # Calculate expected number of chunks
    if chunk_size <= overlap:
        logger.warning("Chunk size should be greater than overlap. Using chunk_size=512, overlap=50")
        chunk_size = 512
        overlap = 50

    # Create chunks of tokens
    chunks = []
    step_size = chunk_size - overlap
    total_steps = max(1, (len(tokens) - overlap + step_size - 1) // step_size)  # Ceiling division

    logger.debug(f"Creating chunks with step size: {step_size}, expected chunks: {total_steps}")

    for i in range(0, len(tokens), step_size):
        # Get token slice
        token_chunk = tokens[i:i + chunk_size]
        # Decode tokens back to text
        text_chunk = tokenizer.decode(token_chunk)
        chunks.append(text_chunk)

        logger.debug(f"Created chunk {len(chunks)} with {len(token_chunk)} tokens")

        # Stop if we've reached the end
        if i + chunk_size >= len(tokens):
            break

    logger.info(f"Successfully created {len(chunks)} token-based chunks")
    return chunks

def chunk_by_sentences_with_token_limit(
    text: str,
    max_tokens: int = 512,
    encoding_name: str = "cl100k_base"
) -> List[str]:
    """
    Split text into sentence-aware chunks respecting token limits with enhanced logging

    Args:
        text (str): Text to chunk
        max_tokens (int): Maximum tokens per chunk
        encoding_name (str): Name of the encoding for tokenization

    Returns:
        List[str]: List of sentence-aware text chunks
    """
    logger.info(f"Chunking text by sentences with max_tokens={max_tokens}, encoding={encoding_name}")

    # Initialize tokenizer
    tokenizer = get_tokenizer(encoding_name)

    # Split text into sentences (simple split by periods)
    sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
    logger.debug(f"Split text into {len(sentences)} sentences")

    chunks = []
    current_chunk = ""

    for sentence_idx, sentence in enumerate(sentences):
        # Check if adding this sentence would exceed token limit
        test_chunk = current_chunk + " " + sentence if current_chunk else sentence
        token_count = len(tokenizer.encode(test_chunk))

        if token_count <= max_tokens:
            current_chunk = test_chunk
            logger.debug(f"Sentence {sentence_idx + 1} fits in current chunk ({token_count} tokens)")
        else:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append(current_chunk.strip())
                logger.debug(f"Saved chunk {len(chunks)} with {len(tokenizer.encode(current_chunk.strip()))} tokens")
            current_chunk = sentence
            logger.debug(f"Started new chunk with sentence {sentence_idx + 1}")

    # Add remaining text as final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
        logger.debug(f"Saved final chunk with {len(tokenizer.encode(current_chunk.strip()))} tokens")

    logger.info(f"Successfully created {len(chunks)} sentence-aware chunks")
    return chunks