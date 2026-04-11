"""
Chat service
Handles chat interactions with grounding on retrieved context
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
import ollama

from .embedding_service import EmbeddingService
from .vector_store import VectorStore
from ..core.config import Config

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat interactions with context grounding"""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[VectorStore] = None,
        ollama_model: str = "llama3"
    ):
        """
        Initialize the chat service

        Args:
            embedding_service (Optional[EmbeddingService]): Embedding service instance
            vector_store (Optional[VectorStore]): Vector store instance
            ollama_model (str): Ollama model name to use for generation
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()
        self.ollama_model = ollama_model
        # In-memory storage for conversation history
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}

    def chat_with_context(self, query: str, context_id: Optional[str] = None, k: int = 5) -> Dict[str, Any]:
        """
        Process a chat query with context grounding

        Args:
            query (str): User query
            context_id (Optional[str]): Conversation context ID
            k (int): Number of relevant chunks to retrieve

        Returns:
            Dict[str, Any]: Response with answer and sources
        """
        try:
            logger.info(f"Processing chat query: {query} with context_id: {context_id}")

            # Get conversation history if context_id is provided
            history = []
            if context_id:
                history = self.conversation_history.get(context_id, [])

            # Step 1: Convert query to embedding
            logger.info("Step 1: Generating query embedding")
            query_embedding = self.embedding_service.embed_text(query)

            # Step 2: Query VectorStore to retrieve top-k relevant chunks
            logger.info(f"Step 2: Retrieving top-{k} relevant chunks")
            results = self.vector_store.query(
                query_embeddings=[query_embedding],
                n_results=k
            )

            # Check if we have any relevant context
            if not results['documents'] or not results['documents'][0]:
                logger.info("No relevant context found")
                answer = "I don't know based on the document"
                response = {
                    "answer": answer,
                    "sources": []
                }

                # Store conversation history
                if context_id:
                    self._store_conversation_turn(context_id, query, answer)

                return response

            # Extract the relevant chunks
            relevant_chunks = results['documents'][0]
            logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks")

            # Combine chunks into context
            context = "\n\n".join(relevant_chunks)
            logger.debug(f"Context for generation: {context[:200]}...")

            # Step 3: Pass retrieved context + user query to Ollama LLM
            logger.info("Step 3: Generating response with Ollama")
            prompt = self._create_prompt(query, context, history)

            response = ollama.generate(
                model=self.ollama_model,
                prompt=prompt,
                options={
                    "temperature": 0.3,  # Lower temperature for more focused responses
                    "top_p": 0.9
                }
            )

            # Step 4: Return grounded response with sources
            answer = response['response'].strip()

            # If the model didn't find information in the context, use our default response
            if not answer or "don't know" in answer.lower() or "not found" in answer.lower():
                answer = "I don't know based on the document"

            logger.info("Response generated successfully")

            response_data = {
                "answer": answer,
                "sources": relevant_chunks
            }

            # Store conversation history
            if context_id:
                self._store_conversation_turn(context_id, query, answer)

            return response_data

        except Exception as e:
            logger.error(f"Error processing chat query: {str(e)}")
            raise

    def stream_chat_with_context(self, query: str, context_id: Optional[str] = None, k: int = 5):
        """
        Process a chat query with context grounding and stream the response

        Args:
            query (str): User query
            context_id (Optional[str]): Conversation context ID
            k (int): Number of relevant chunks to retrieve

        Yields:
            dict: Response chunks from the Ollama LLM with metadata
        """
        try:
            logger.info(f"Processing streaming chat query: {query} with context_id: {context_id}")

            # Get conversation history if context_id is provided
            history = []
            if context_id:
                history = self.conversation_history.get(context_id, [])

            # Step 1: Convert query to embedding
            logger.info("Step 1: Generating query embedding")
            query_embedding = self.embedding_service.embed_text(query)

            # Step 2: Query VectorStore to retrieve top-k relevant chunks
            logger.info(f"Step 2: Retrieving top-{k} relevant chunks")
            results = self.vector_store.query(
                query_embeddings=[query_embedding],
                n_results=k
            )

            # Extract the relevant chunks (sources)
            relevant_chunks = []
            if results['documents'] and results['documents'][0]:
                relevant_chunks = results['documents'][0]

            logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks")

            # Check if we have any relevant context
            if not relevant_chunks:
                logger.info("No relevant context found")
                answer = "I don't know based on the document"

                # Store conversation history
                if context_id:
                    self._store_conversation_turn(context_id, query, answer)

                # Yield the answer and sources
                yield {"type": "content", "value": answer}
                yield {"type": "sources", "value": []}
                return

            # Combine chunks into context
            context = "\n\n".join(relevant_chunks)
            logger.debug(f"Context for generation: {context[:200]}...")

            # Step 3: Pass retrieved context + user query to Ollama LLM with streaming
            logger.info("Step 3: Generating streaming response with Ollama")
            prompt = self._create_prompt(query, context, history)

            response_stream = ollama.generate(
                model=self.ollama_model,
                prompt=prompt,
                stream=True,
                options={
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            )

            # Collect the full response for conversation history
            full_response = ""

            # Stream response chunks
            for chunk in response_stream:
                if 'response' in chunk:
                    chunk_text = chunk['response']
                    full_response += chunk_text
                    yield {"type": "content", "value": chunk_text}

            # Check if response is meaningful
            stripped_response = full_response.strip()
            if not stripped_response or "don't know" in stripped_response.lower() or "not found" in stripped_response.lower():
                default_response = "I don't know based on the document"
                if context_id:
                    self._store_conversation_turn(context_id, query, default_response)
                # Only yield the default response if we haven't already yielded content
                if not full_response.strip():
                    yield {"type": "content", "value": default_response}
            else:
                # Store conversation history with the full response
                if context_id:
                    self._store_conversation_turn(context_id, query, stripped_response)

            # Yield sources at the end
            yield {"type": "sources", "value": relevant_chunks}
            yield {"type": "end", "value": True}

        except Exception as e:
            logger.error(f"Error processing streaming chat query: {str(e)}")
            error_msg = f"Error: {str(e)}"
            yield {"type": "content", "value": error_msg}

    def _create_prompt(self, query: str, context: str, history: List[Dict[str, str]]) -> str:
        """
        Create a strict prompt for the LLM with the query, context, and history

        Args:
            query (str): User query
            context (str): Retrieved context
            history (List[Dict[str, str]]): Conversation history

        Returns:
            str: Formatted prompt with strict instructions
        """
        # Build conversation history string
        history_str = ""
        if history:
            history_str = "\nCONVERSATION HISTORY:\n"
            for i, turn in enumerate(history[-5:], 1):  # Last 5 turns
                history_str += f"{i}. User: {turn['query']}\n"
                history_str += f"   Assistant: {turn['answer']}\n"

        prompt = f"""You are a precise assistant that answers questions based EXCLUSIVELY on the provided context.

STRICT INSTRUCTIONS:
1. ONLY use information explicitly stated in the provided context
2. DO NOT use any outside knowledge or make assumptions
3. DO NOT hallucinate or infer information not directly stated
4. If the answer is not explicitly found in the context, respond with: "I don't know based on the document"
5. Keep your answer concise and directly relevant to the question
6. Consider the conversation history when relevant, but still only use information from the provided context

CONTEXT:
{context}{history_str}

QUESTION: {query}

ANSWER:"""
        return prompt

    def _store_conversation_turn(self, context_id: str, query: str, answer: str) -> None:
        """
        Store a conversation turn in history

        Args:
            context_id (str): Conversation context ID
            query (str): User query
            answer (str): Assistant answer
        """
        if context_id not in self.conversation_history:
            self.conversation_history[context_id] = []

        self.conversation_history[context_id].append({
            "query": query,
            "answer": answer
        })

        # Keep only the last 10 turns to prevent memory issues
        if len(self.conversation_history[context_id]) > 10:
            self.conversation_history[context_id] = self.conversation_history[context_id][-10:]

    def get_conversation_history(self, context_id: str) -> List[Dict[str, str]]:
        """
        Get conversation history for a context ID

        Args:
            context_id (str): Conversation context ID

        Returns:
            List[Dict[str, str]]: Conversation history
        """
        return self.conversation_history.get(context_id, [])