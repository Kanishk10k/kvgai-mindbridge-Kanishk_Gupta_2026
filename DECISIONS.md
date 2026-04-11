MindBridge – Design Decisions

1. Chunking Strategy
I implemented token-based chunking instead of character-based chunking.

Token-based chunking aligns with how LLMs process input
Ensures better utilization of context window
Prevents breaking semantic meaning mid-token

I initially considered character-based chunking, but rejected it because it can lead to inconsistent context sizes and reduced retrieval quality.

2. Embedding Model Selection
I used all-MiniLM-L6-v2 from SentenceTransformers.

Reasons:
Lightweight and fast (important for local setup)
Good semantic similarity performance for general text
Works well without GPU

Tradeoff:
Not as powerful as larger embedding models, but sufficient for this use case

3. Vector Database Choice
I selected ChromaDB as the vector store.

Reasons:
Easy local setup (no external service required)
Persistent storage support
Good integration with Python ecosystem

Alternative considered:
FAISS (faster but less convenient for persistence)
Pinecone (rejected due to external dependency)

4. Retrieval Strategy
I used top-k similarity search (default k=5).

Reasons:
Simple and effective for most queries
Balances recall and precision

Limitations:
No reranking or hybrid search (BM25 + embeddings)
Could retrieve slightly irrelevant chunks in edge cases

5. Grounding and Hallucination Control
I enforced strict grounding using prompt design:
Model is instructed to use ONLY provided context
Explicit fallback:
"I don't know based on the document"

Additionally:
Post-response validation ensures weak answers are replaced

6. Conversation Memory Design
I implemented in-memory conversation history using context_id.

Features:
Supports multi-turn conversations
Maintains last 10 interactions

Tradeoff:
Memory resets on server restart (not persistent)

Reason:
Simplicity and faster implementation

7. Context Reset Strategy
Instead of automatic reset, I implemented:
Manual "Reset Context" button
Keyword-based reset (e.g., "reset", "clear context")

Reason:
Preserves conversation continuity
Gives user control over context lifecycle

8. Streaming Response (Bonus Feature)
I implemented streaming using Ollama's streaming API.

Backend:
Generator-based streaming with FastAPI StreamingResponse
JSONL structured chunks (content, sources, end)

Frontend:
Simulated typing effect using Streamlit

Benefits:
Improved user experience
Reduced perceived latency

9. Frontend Choice
I used Streamlit for frontend.

Reasons:
Rapid development
Easy integration with backend APIs
Suitable for demo and prototyping

Tradeoff:
Less flexible than React/Next.js
Limited real-time capabilities

10. Error Handling
Implemented at multiple levels:
API-level exception handling (FastAPI)
Frontend error messages
Backend logging

11. Limitations
In-memory conversation storage (not persistent)
Basic retrieval (no reranking)
No document-level filtering
Depends on local Ollama setup
Streamlit limits real-time UI capabilities

12. Use of AI Tools
I used AI tools (primarily Claude) for:
Code scaffolding
Debugging assistance
Design suggestions


However:
All architectural decisions were made consciously
Code was reviewed and refined manually
Prompts were iteratively improved to ensure correctness