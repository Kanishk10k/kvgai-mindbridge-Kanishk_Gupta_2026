import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './ChatComponent.css';

const ChatComponent = ({ documentId }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversation history on component mount
  useEffect(() => {
    loadConversationHistory();
  }, [documentId]);

  const loadConversationHistory = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/chat/history/${documentId}`);
      if (response.data.messages && response.data.messages.length > 0) {
        // Format messages for display
        const formattedMessages = response.data.messages.map(msg => ({
          role: msg.role || (msg.query ? 'user' : 'assistant'),
          content: msg.query || msg.answer || msg.content
        }));
        setMessages(formattedMessages);
      }
    } catch (err) {
      console.log('No conversation history found or error loading history');
      // This is not a critical error, so we don't show it to the user
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || loading) return;

    const userMessage = { role: 'user', content: inputValue };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);
    setError(null);

    try {
      // Try streaming first, fallback to regular response
      const response = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: inputValue,
          context_id: documentId
        }),
      });

      if (response.ok && response.body) {
        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        const aiMessage = { role: 'assistant', content: '' };
        setMessages(prev => [...prev, aiMessage]);

        let accumulatedContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n').filter(line => line.trim());

          for (const line of lines) {
            try {
              const data = JSON.parse(line);
              if (data.type === 'content') {
                accumulatedContent += data.value;
                // Update the last message with accumulated content
                setMessages(prev => {
                  const newMessages = [...prev];
                  newMessages[newMessages.length - 1] = {
                    ...newMessages[newMessages.length - 1],
                    content: accumulatedContent
                  };
                  return newMessages;
                });
              } else if (data.type === 'end') {
                // Streaming is complete
                break;
              }
            } catch (parseError) {
              // Ignore parsing errors for individual lines
              console.warn('Error parsing streaming chunk:', parseError);
            }
          }
        }
      } else {
        // Fallback to regular response
        const jsonResponse = await response.json();
        const aiMessage = { role: 'assistant', content: jsonResponse.answer };
        setMessages(prev => [...prev, aiMessage]);
      }
    } catch (err) {
      const errorMessage = { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' };
      setMessages(prev => {
        const newMessages = [...prev];
        // Replace the last message if it's the one we just added
        if (newMessages.length > 0 && newMessages[newMessages.length - 1].role === 'assistant' &&
            newMessages[newMessages.length - 1].content === '') {
          newMessages[newMessages.length - 1] = errorMessage;
        } else {
          newMessages.push(errorMessage);
        }
        return newMessages;
      });
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-component">
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">
              {message.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask a question about the document..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !inputValue.trim()}>
          Send
        </button>
      </form>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default ChatComponent;