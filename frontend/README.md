# MindBridge Frontend

This is the frontend for the MindBridge document-based Q&A system.

## Prerequisites

- Node.js (version 14 or higher)
- npm (comes with Node.js)

## Installation

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

## Running the Application

1. Make sure the backend API is running on `http://localhost:8000`
2. Start the frontend development server:
   ```
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

## Features

- Drag and drop PDF file upload
- Chat interface for asking questions about uploaded documents
- Real-time responses grounded in document content
- Conversation history retention

## Development

The frontend is built with React and communicates with the backend API endpoints:

- POST `/upload/` - Upload PDF documents
- POST `/chat/message` - Send chat messages and receive responses
- GET `/chat/history/{context_id}` - Retrieve chat history

## Folder Structure

```
frontend/
├── public/                 # Static files
├── src/                    # React source code
│   ├── components/         # React components
│   ├── App.js              # Main App component
│   ├── App.css             # App styles
│   └── index.js            # Entry point
├── package.json           # Dependencies and scripts
└── README.md              # This file
```