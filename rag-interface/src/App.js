import React, { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [useRerank, setUseRerank] = useState(false);

  // Real API call function
  const callRagApi = async (question, useRerank = false) => {
    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: question,
          use_rerank: useRerank 
        }),
      });
      
      if (!response.ok) {
        throw new Error('API request failed');
      }
      
      return await response.json();
    } catch (error) {
      console.error('API call failed:', error);
      // Fallback to mock data if API is not available
      return {
        answer: `This is a mock response to: "${question}". Make sure your Python backend is running on port 8000.`,
        sources: [
          {
            id: 1,
            title: 'Sample Document 1',
            content: 'Relevant content from document 1...',
            similarity: 0.95
          },
          {
            id: 2,
            title: 'Sample Document 2', 
            content: 'Relevant content from document 2...',
            similarity: 0.87
          }
        ],
        query: question
      };
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    
    try {
      const result = await callRagApi(query, useRerank);
      
      setResponse(result.answer);
      setSources(result.sources);
      
      // Add to chat history
      setChatHistory(prev => [...prev, {
        question: query,
        answer: result.answer,
        sources: result.sources,
        timestamp: new Date().toLocaleTimeString(),
      }]);
      
      setQuery('');
    } catch (error) {
      console.error('Error:', error);
      setResponse('Sorry, there was an error processing your request.');
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setChatHistory([]);
    setResponse('');
    setSources([]);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>RAG Interface MVP</h1>
        <p>Ask questions and get AI-powered answers with source references</p>
      </header>

      <div className="app-container">
        {/* Chat History */}
        <div className="chat-history">
          <div className="history-header">
            <h3>Conversation History</h3>
            <button onClick={clearChat} className="clear-btn">
              Clear Chat
            </button>
          </div>
          <div className="history-content">
            {chatHistory.length === 0 ? (
              <p className="empty-state">No conversation yet. Ask a question to get started!</p>
            ) : (
              chatHistory.map((chat, index) => (
                <div key={index} className="chat-item">
                  <div className="question">
                    <strong>Q: </strong>{chat.question}
                    <span className="timestamp">{chat.timestamp}</span>
                  </div>
                  <div className="answer">
                    <strong>A: </strong>{chat.answer}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="main-content">
          {/* Input Form */}
          <form onSubmit={handleSubmit} className="query-form">
            <div className="input-group">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question..."
                disabled={loading}
                className="query-input"
              />
              <button 
                type="submit" 
                disabled={loading || !query.trim()}
                className="submit-btn"
              >
                {loading ? 'Thinking...' : 'Ask'}
              </button>
            </div>
          </form>

          {/* Current Response */}
          {response && (
            <div className="response-section">
              <h3>Response</h3>
              <div className="response-content">
                {response}
              </div>
            </div>
          )}

          {/* Sources */}
          {sources.length > 0 && (
            <div className="sources-section">
              <h3>Sources ({sources.length} found)</h3>
              <div className="sources-list">
                {sources.map((source) => (
                  <div key={source.id} className="source-item">
                    <div className="source-header">
                      <span className="source-title">{source.title}</span>
                    </div>
                    <div className="source-content">
                      {source.content}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;