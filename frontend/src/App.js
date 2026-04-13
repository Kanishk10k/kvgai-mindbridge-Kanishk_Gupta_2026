import React, { useState } from 'react';
import './App.css';
import UploadComponent from './components/UploadComponent';
import ChatComponent from './components/ChatComponent';

function App() {
  const [uploadedDocument, setUploadedDocument] = useState(null);

  const handleDocumentUpload = (documentData) => {
    setUploadedDocument(documentData);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>MindBridge</h1>
        <p>Document-based Question Answering System</p>
      </header>

      <main>
        <section className="upload-section">
          <h2>Upload Document</h2>
          <UploadComponent onUploadSuccess={handleDocumentUpload} />
        </section>

        {uploadedDocument && (
          <section className="chat-section">
            <h2>Chat with Document</h2>
            <ChatComponent documentId={uploadedDocument.document_id} />
          </section>
        )}
      </main>

      <footer>
        <p>MindBridge - Document-based Q&A System</p>
      </footer>
    </div>
  );
}

export default App;