from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from ..services.chat_service import ChatService

router = APIRouter()

logger = logging.getLogger(__name__)

# Global chat service instance
chat_service = ChatService()

class ChatMessage(BaseModel):
    """Chat message model"""
    role: str
    content: str

class ChatRequest(BaseModel):
    """Chat request model"""
    query: str
    context_id: Optional[str] = None
    k: Optional[int] = 5

class ChatResponse(BaseModel):
    """Chat response model"""
    answer: str
    sources: List[str]

class ChatHistoryResponse(BaseModel):
    """Chat history response model"""
    context_id: str
    messages: List[Dict[str, str]]
    message: str

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Process a chat message with context grounding

    Args:
        request (ChatRequest): The chat request containing the query and context_id

    Returns:
        ChatResponse: The chat response with answer and sources
    """
    try:
        # Process the query and get response with sources
        result = chat_service.chat_with_context(
            query=request.query,
            context_id=request.context_id,
            k=request.k
        )

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")

@router.get("/history/{context_id}", response_model=ChatHistoryResponse)
async def get_chat_history(context_id: str):
    """
    Get chat history for a context

    Args:
        context_id (str): The context ID to retrieve history for

    Returns:
        ChatHistoryResponse: Chat history
    """
    try:
        # Get conversation history from chat service
        history = chat_service.get_conversation_history(context_id)

        return ChatHistoryResponse(
            context_id=context_id,
            messages=history,
            message="Chat history retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")