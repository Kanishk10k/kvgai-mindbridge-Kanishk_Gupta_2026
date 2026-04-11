# 📚 MindBridge - Document Q&A System

MindBridge is a Retrieval-Augmented Generation (RAG) based application that allows users to upload PDF documents and ask questions about their content. The system retrieves relevant information from the document and generates accurate, context-based answers using a local LLM.

---

## 🚀 Features

- 📄 Upload PDF documents
- 🔍 Context-aware question answering
- 🧠 Semantic search using embeddings
- ⚡ Streaming responses for better UX
- 📚 Source-based answers (explainability)
- 💬 Multi-turn conversation support

---

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **LLM:** Ollama (LLaMA 3)
- **Embeddings:** Sentence Transformers
- **Vector DB:** ChromaDB
- **PDF Processing:** PyPDF

---

## 📁 Project Structure

```
mindbridge/
│
├── app.py                 # Streamlit frontend
├── requirements.txt
├── README.md
│
├── backend/
│   └── app/
│       ├── main.py        # FastAPI entry point
│       ├── core/          # Config and initialization
│       ├── routes/        # API endpoints (upload, chat)
│       ├── services/      # Business logic (RAG pipeline)
│       └── utils/         # Helpers (chunking, PDF loader)
│
└── data/raw/              # Uploaded PDF storage
```

---

## ⚙️ Prerequisites

Make sure you have the following installed:

- Python **3.12**
- Conda (recommended)
- Ollama installed

### Install Ollama:
👉 https://ollama.com/

---

## 🧪 Setup Instructions

### 1. Clone the repository

```bash
git clone <https://github.com/Kanishk10k/mindbridge.git>
cd mindbridge
```

### 2. Create and activate environment

```bash
conda create -p venv python==3.12 -y
conda activate ./venv
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Ollama

Start Ollama:

```bash
ollama serve
```

Pull required model:

```bash
ollama pull llama3
```

---

## ▶️ Running the Application

### 1. Start Backend (FastAPI)

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Check:
👉 http://localhost:8000/health

### 2. Start Frontend (Streamlit)

```bash
streamlit run app.py
```

---

## 💡 How to Use

1. Open the Streamlit app in browser
2. Upload a PDF document
3. Ask questions like:
   - "What is this document about?"
   - "Summarize the key points"
   - "Explain section 2"
4. Get answers grounded in document content with sources

---

## ⚠️ Important Notes

- Backend must be running before frontend
- Ollama must be running for LLM responses
- This project is designed for local execution only
- No external APIs are used (fully offline capable)

---

## 🧩 Known Limitations

- Requires local setup (not cloud-hosted)
- Depends on Ollama running locally
- Basic retrieval (no reranking)
- In-memory chat history (not persistent)

---

## 🛠️ Troubleshooting

### 🔴 Backend not starting
- Check dependencies installed correctly
- Verify correct Python version

### 🔴 Ollama not responding
```bash
ollama serve
```

### 🔴 Model not found
```bash
ollama pull llama3
```

### 🔴 Port already in use

Change port:

```bash
uvicorn backend.app.main:app --port 8001
```

### 🔴 Empty responses
- Ensure document is uploaded
- Check embedding and vector store logs

---

## 🧠 How It Works (RAG Pipeline)

1. PDF is uploaded
2. Text is extracted
3. Text is chunked (token-based)
4. Embeddings are generated
5. Stored in ChromaDB
6. Query is embedded
7. Relevant chunks retrieved
8. Context + query sent to LLM
9. Answer generated and streamed

---

## 🚀 Future Improvements

- Persistent chat history (DB)
- Multi-document support
- Semantic chunking
- UI enhancements
- Cloud deployment support