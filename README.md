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
- 🖥️ Modern React frontend (replaces Streamlit)

---
## 🛠️ Tech Stack

- **Backend:** FastAPI
- **Frontend:** React.js
- **LLM:** Ollama (LLaMA 3)
- **Embeddings:** Sentence Transformers
- **Vector DB:** ChromaDB
- **PDF Processing:** PyPDF

---
## 📁 Project Structure

```
mindbridge/
│
├── backend/                 # FastAPI backend
│   └── app/
│       ├── main.py         # FastAPI entry point
│       ├── core/           # Config and initialization
│       ├── routes/         # API endpoints (upload, chat)
│       ├── services/       # Business logic (RAG pipeline)
│       └── utils/          # Helpers (chunking, PDF loader)
│
├── frontend/               # React frontend
│   ├── public/             # Static files
│   ├── src/                # React source code
│   │   ├── components/     # React components
│   │   ├── App.js          # Main App component
│   │   └── index.js        # Entry point
│   └── package.json        # Frontend dependencies
│
├── data/raw/               # Uploaded PDF storage
├── .env                    # Environment configuration
└── README.md              # This file
```

---
## ⚙️ Prerequisites

Make sure you have the following installed:

- Python **3.12**
- Node.js **14+**
- Conda (recommended)
- Ollama installed

### Install Ollama:
👉 https://ollama.com/

---
## 🧪 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Kanishk10k/mindbridge.git
cd mindbridge
```

### 2. Create and activate environment

```bash
conda create -p venv python==3.12 -y
conda activate ./venv
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Setup Ollama

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

### 2. Start Frontend (React)

In a new terminal:

```bash
cd frontend
npm start
```

Frontend will be available at:
👉 http://localhost:3000

---
## 💡 How to Use

1. Open the React app in browser (http://localhost:3000)
2. Upload a PDF document using drag & drop
3. Wait for processing to complete
4. Ask questions in the chat interface
5. Get answers grounded in document content with sources

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

1. PDF is uploaded via React frontend
2. Text is extracted
3. Text is chunked (token-based)
4. Embeddings are generated
5. Stored in ChromaDB
6. Query is embedded
7. Relevant chunks retrieved
8. Context + query sent to LLM
9. Answer generated and streamed to frontend

---
## 🚀 Future Improvements

- Persistent chat history (DB)
- Multi-document support
- Semantic chunking
- UI enhancements
- Cloud deployment support