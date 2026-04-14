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

- Drag and drop PDF file upload with validation
- Chat interface for asking questions about uploaded documents
- Real-time streaming responses grounded in document content
- Conversation history retention
- Responsive design for desktop and mobile devices
- Visual feedback for all user interactions

## Development

The frontend is built with React and communicates with the backend API endpoints:

- POST `/upload/` - Upload PDF documents
- POST `/chat/message` - Send chat messages and receive responses
- POST `/chat/stream` - Send chat messages and stream responses
- GET `/chat/history/{context_id}` - Retrieve chat history

## Folder Structure

```
frontend/
├── public/                 # Static files
│   └── index.html         # Main HTML file
├── src/                    # React source code
│   ├── components/         # React components
│   │   ├── UploadComponent.js     # File upload component
│   │   ├── UploadComponent.css    # Upload component styles
│   │   ├── ChatComponent.js       # Chat interface component
│   │   └── ChatComponent.css      # Chat component styles
│   ├── App.js              # Main App component
│   ├── App.css             # App styles
│   ├── index.js            # Entry point
│   └── index.css           # Base styles
├── package.json           # Dependencies and scripts
└── README.md              # This file
```

## Component Details

### UploadComponent
- Provides drag-and-drop file upload interface
- Validates PDF files and file size limits
- Shows upload progress and results
- Handles error states gracefully

### ChatComponent
- Interactive chat interface with message history
- Supports streaming responses for real-time feedback
- Maintains conversation context
- Displays sources for answers

### App Component
- Main application layout and routing
- Manages global state between components
- Provides header and footer elements

## Styling

The frontend uses plain CSS for styling with:
- Responsive design principles
- Modern color scheme and typography
- Accessible contrast ratios
- Mobile-first approach

## API Integration

The frontend communicates with the backend using:
- Axios for HTTP requests
- Fetch API for streaming responses
- Proper error handling for network issues
- Loading states for better UX

## Environment Configuration

The frontend expects the backend to be available at:
- `http://localhost:8000` (default)
- All API endpoints are relative to this base URL

## Development Commands

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests (if available)
npm test

# Eject from react-scripts (not recommended)
npm run eject
```