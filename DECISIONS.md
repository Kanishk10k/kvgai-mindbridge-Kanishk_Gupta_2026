#  MindBridge – Design Decisions

---

## 1. Chunking Strategy

I implemented **token-based chunking** instead of character-based chunking.

### Reasons:
- Aligns with how LLMs process input (tokens, not characters)
- Ensures efficient use of context window
- Prevents breaking semantic meaning mid-token

### Alternative Considered:
- Character-based chunking

### Why Rejected:
- Inconsistent context sizes
- Lower retrieval quality

---

## 2. Embedding Model Selection

I used **all-MiniLM-L6-v2** from SentenceTransformers.

### Reasons:
- Lightweight and fast (suitable for local setup)
- Good semantic similarity performance
- Works efficiently without GPU

### Tradeoff:
- Less powerful than larger embedding models

---

## 3. Vector Database Choice

I selected **ChromaDB** as the vector store.

### Reasons:
- Simple local setup (no external service required)
- Persistent storage support
- Easy Python integration

### Alternatives Considered:
- FAISS → faster but less convenient persistence
- Pinecone → rejected due to external dependency

---

## 4. Retrieval Strategy

I implemented **top-k similarity search** (k = 5).

### Reasons:
- Simple and effective
- Balances recall and precision

### Limitations:
- No reranking
- No hybrid search (BM25 + embeddings)
- Possible irrelevant chunks in edge cases

---

## 5. Grounding and Hallucination Control

I enforced strict grounding using prompt design.

### Approach:
- Model instructed to use ONLY provided context
- Explicit fallback:
  > "I don't know based on the document"

### Additional Safeguard:
- Post-response validation to filter weak answers

---

## 6. Conversation Memory Design

I implemented **in-memory conversation history** using `context_id`.

### Features:
- Supports multi-turn conversations
- Stores last 10 interactions

### Tradeoff:
- Not persistent (resets on restart)

### Reason:
- Simplicity and faster implementation

---

## 7. Context Reset Strategy

Implemented manual and keyword-based reset:

- "Reset Context" button
- Keywords like: "reset", "clear context"

### Reason:
- Prevents unwanted context carryover
- Gives user explicit control

---

## 8. Streaming Response (Bonus Feature)

Implemented streaming using **Ollama streaming API**.

### Backend:
- Generator-based streaming
- FastAPI `StreamingResponse`
- JSONL format (`content`, `sources`, `end`)

### Frontend:
- Simulated typing effect using Streamlit

### Benefits:
- Better user experience
- Reduced perceived latency

---

## 9. Frontend Choice

Used **Streamlit** for frontend.

### Reasons:
- Rapid development
- Easy API integration
- Ideal for prototyping and demos

### Tradeoff:
- Less flexible than modern frontend frameworks
- Limited UI control

---

## 10. Error Handling

Implemented multi-layer error handling:

- FastAPI exception handling
- Backend logging
- Streamlit UI error display

---

## 11. System Limitations

- In-memory conversation storage
- Basic retrieval (no reranking)
- No document-level filtering
- Requires local Ollama setup
- Limited frontend scalability

---

## 12. Use of AI Tools

Used AI tools (primarily Claude) for:

- Code scaffolding
- Debugging
- Design suggestions

### Important:
- All architectural decisions were made manually
- Code was reviewed and refined
- Prompts were iteratively improved

---

## 13. Deployment Challenges and Solutions

Initially attempted deployment using Streamlit Cloud.

### Issue:
- Backend running on localhost was not accessible

### Solution:
- Used ngrok to expose local backend
- Updated API endpoints to ngrok URL

---

## 14. ngrok Security Handling

Encountered browser warning blocking API requests.

### Solution:
- Added header:
  ```text
  ngrok-skip-browser-warning: true
  ```

---

## 15. Connectivity Debugging Learnings

Encountered:

- Connection refused
- ERR_NGROK_8012
- DNS issues (trailing spaces)

Key Learnings:
- Backend must run before ngrok
- URLs must be exact (no trailing spaces)
- Always validate /health endpoint

---

## 16. Backend Dependency Issues

Encountered runtime failures due to:

- Ollama not running
- Model not loaded

Solution:
- Ensured ollama serve is active
- Verified model availability

---

## 17. Dependency Version Conflicts

Faced compatibility issues between:

- sentence-transformers
- transformers
- huggingface_hub

Solution:

Aligned versions:

```text
sentence-transformers==2.2.2
transformers==4.30.2
huggingface_hub==0.14.1
```

---

## 18. Module Import Conflict

Faced import issue due to naming conflict:

- app.py (frontend)
- app/ (backend package)

Problem:
- Python imported wrong module

Solution:

Used fully qualified imports:

```python
from backend.app.routes import ...
```

---

## 19. Architecture Overview

The system follows a Retrieval-Augmented Generation (RAG) pipeline:

1. User uploads PDF
2. Text extraction
3. Token-based chunking
4. Embedding generation
5. Storage in ChromaDB
6. Query embedding
7. Top-k retrieval
8. Context + query sent to LLM
9. Response generation
10. Streaming to frontend

Benefits:
- Context-aware responses
- Reduced hallucination
- Explainable answers via sources

---

## 20. Practical Learnings

Through this project, I gained experience in:

- RAG system design
- API development with FastAPI
- Streamlit frontend integration
- Handling dependency conflicts
- Debugging distributed systems
- Understanding local vs cloud tradeoffs

---
