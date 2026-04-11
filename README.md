# MindBridge

An intelligent document-based question answering system built with FastAPI, ChromaDB, and Ollama.

## Overview

MindBridge allows users to upload PDF documents and ask questions about their content. The system uses embeddings and vector search to retrieve relevant context, then leverages a local LLM to generate grounded responses.

## Features

- PDF document upload and processing
- Semantic search using vector embeddings
- Context-grounded question answering
- Conversation history support
- RESTful API with FastAPI

## Architecture

The system consists of:

1. **Document Ingestion Pipeline**
   - PDF text extraction
   - Intelligent chunking
   - Embedding generation
   - Vector storage

2. **Chat System**
   - Query embedding and search
   - Context retrieval
   - LLM-based response generation
   - Conversation history management

## Technologies

- **FastAPI** - High-performance web framework
- **ChromaDB** - Vector database for similarity search
- **Sentence Transformers** - Embedding generation
- **Ollama** - Local LLM inference
- **PyPDF** - PDF processing

## Access the deployed webapp using this following link

https://kanishk10k-mindbridge-app-of8d1j.streamlit.app/

## API Endpoints

- `POST /upload/` - Upload and process PDF documents
- `DELETE /upload/{file_id}` - Delete a document
- `POST /chat/message` - Ask questions about uploaded documents
- `GET /chat/history/{context_id}` - Retrieve conversation history

## Future Work

- Frontend implementation with React
- Enhanced document processing capabilities
- Multi-user support
- Advanced analytics and monitoring
