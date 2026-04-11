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

13. Deployment Challenges and Solutions
While deploying the frontend using Streamlit Cloud, I encountered issues with backend connectivity.

Initially, the frontend was configured to call:

http://localhost:8000

However, this failed because:
Streamlit Cloud runs on a remote server
localhost refers to the server itself, not my local machine
Solution:

I used ngrok to expose my local FastAPI backend to the internet.
Created a public URL using ngrok
Updated the frontend API base URL to use the ngrok endpoint

14. Handling ngrok Security Restrictions
While using ngrok, I encountered a browser warning page that blocked API requests.

This affected programmatic calls from the frontend.

Solution:
I added a custom header to all API requests:
"ngrok-skip-browser-warning": "true"

This bypassed the warning and allowed seamless communication between frontend and backend.

15. Debugging Connectivity Issues
During integration, I encountered multiple connectivity errors:

Issues:
Connection refused
ERR_NGROK_8012
DNS resolution errors caused by incorrect URL formatting (trailing spaces)
Learnings:
Backend must be running before starting ngrok
ngrok URL must be updated correctly without extra spaces
Always validate endpoints using /health

16. Handling Backend Dependency Failures
I observed 503 Service Unavailable errors during file upload.

Root Cause:
The backend depends on a locally running LLM (Ollama).
If Ollama is not running or the model is not loaded, the backend fails.

Solution:
Ensured Ollama service is running (ollama serve)
Verified model availability before making requests

17. System Design Limitation
The current system has a key limitation:
The backend depends on a locally running LLM (Ollama)
The deployed frontend cannot function independently
The system requires:
Local backend running
ngrok active
Ollama running

Tradeoff:
This approach was chosen to:
Avoid external API costs
Maintain full control over the model

However, it reduces deployment robustness compared to fully cloud-hosted solutions.

18. Practical Learnings
Through this project, I gained hands-on experience in:
Deploying frontend and backend separately
Handling real-world networking issues
Debugging distributed system failures
Understanding limitations of local vs cloud architectures