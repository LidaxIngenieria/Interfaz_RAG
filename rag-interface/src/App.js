import React, { useState, useEffect, useRef } from 'react';
import './App.css';
// Import your PNG image
import lidaxLogo from './Lidax_logo.svg'; 





function App() {
  const BACKEND_URL = "http://192.168.1.163:8000";
  const SOURCE_LENGHT = 300;
  const [query, setQuery] = useState('');
  const [pendingQuery, setPendingQuery] = useState(''); // Holds the query that is currently being processed
  const [response, setResponse] = useState('');
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const chatFeedRef = useRef(null); // Renamed from historyContentRef
  const [darkMode, setDarkMode] = useState(false);

  // Load saved theme preference
  useEffect(() => {
    const savedMode = localStorage.getItem("darkMode") === "true";
    setDarkMode(savedMode);
  }, []);

  // Apply dark mode class + save preference
  useEffect(() => {
    document.body.classList.toggle("dark-mode", darkMode);
    localStorage.setItem("darkMode", darkMode);
  }, [darkMode]);

  // Auto-scroll chat history feed
  useEffect(() => {
    if (chatFeedRef.current) {
      chatFeedRef.current.scrollTop = chatFeedRef.current.scrollHeight;
    }
    // Scroll on new history items AND on new streaming chunks
  }, [chatHistory, response]); 


  // Streamed API call (One-Call JSONL approach)
  // ... (This function remains exactly the same as in your original code) ...
  const callRagApiStream = async (question, onChunk, onFinal) => {
    try {
      console.log("Starting stream request (JSONL)...");
        const response = await fetch(`${BACKEND_URL}/query/stream`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: question }),
        });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = ''; 
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log("Stream completed.");
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        let lines = buffer.split('\n');
        buffer = lines.pop(); 

        for (const line of lines) {
            if (!line.trim()) continue;
            try {
                const item = JSON.parse(line);
                if (item.type === 'chunk') {
                    onChunk(item.content);
                } else if (item.type === 'final') {
                    onFinal(item.sources);
                } else if (item.type === 'error') {
                    throw new Error(item.message);
                }
            } catch (error) {
                console.error("Failed to parse JSONL line:", error);
            }
        }
      }
      
      if (buffer.trim()) {
          try {
              const item = JSON.parse(buffer.trim());
              if (item.type === 'final') {
                  onFinal(item.sources);
              }
          } catch (error) {
              console.warn("Remaining buffer was not valid JSON:", error);
          }
      }
    } catch (error) {
      console.error("Streaming error:", error);
      throw error;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const currentQuery = query.trim();
    if (!currentQuery) return;

    setLoading(true);
    setResponse(""); 
    setSources([]); 
    setPendingQuery(currentQuery); // <-- Display the user's question immediately
    setQuery(""); // <-- Clear the input field
    
    let streamedAnswer = "";
    let finalSources = [];

    try {
      // Stream the answer and capture final data
      await callRagApiStream(
        currentQuery, 
        (chunk) => {
          // Callback for chunks (Text)
          streamedAnswer += chunk;
          setResponse(streamedAnswer); 
        }, 
        (sources) => {
          // Callback for final item (Sources)
          finalSources = sources;
          setSources(sources);
        }
      );

      // Add the COMPLETED exchange to history
      setChatHistory(prev => [
        ...prev,
        {
          question: currentQuery,
          answer: streamedAnswer,
          sources: finalSources, 
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
      ]);
      
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = `Sorry, there was an error processing your request: ${error.message}`;
      // Add the ERROR exchange to history
      setChatHistory(prev => [
        ...prev,
        {
          question: currentQuery,
          answer: errorMessage,
          sources: [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
      ]);
    } finally {
      // Clear the "pending" states, as this Q&A is now in the history
      setPendingQuery("");
      setResponse("");
      setSources([]);
      setLoading(false);
    }
  };

  const clearChat = () => {
    setChatHistory([]);
    setPendingQuery('');
    setResponse('');
    setSources([]);
  };

  return (
    <div className="app">
      <header className="app-header">
        <img 
          src={lidaxLogo} 
          alt="Lidax" 
          className="logo-image"
        />
        <div className="header-controls">
          <button 
            onClick={clearChat} 
            className="clear-btn"
            aria-label="Clear chat history"
          >
            Clear
          </button>
          <button 
            className="theme-toggle" 
            onClick={() => setDarkMode(!darkMode)} 
            aria-label="Toggle dark mode"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {/* This container holds the scrolling feed and the fixed input form */}
      <div className="chat-container">

        {/* This is the scrolling chat feed */}
        <div className="chat-feed" ref={chatFeedRef}>
          {chatHistory.length === 0 && !pendingQuery && (
            <p className="empty-state">Your conversation will appear here.</p>
          )}

          {/* 1. Render all completed chat items */}
          {chatHistory.map((chat, index) => (
            <div key={index} className="chat-item">
              <div className="question">
                {chat.question}
                <span className="timestamp">{chat.timestamp}</span>
              </div>
              <div className="answer">
                {chat.answer}
              </div>
              {chat.sources && chat.sources.length > 0 && (
                <div className="sources-section">
                  <h3 className="section-header-inline">Sources ({chat.sources.length})</h3>
                  <div className="sources-list">
                    {chat.sources.map((source, sIndex) => (
                      <div key={sIndex} className="source-item">
                        <a 
                          href={source.link || "#"} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="source-link"
                        >
                          {source.title || `Source ${sIndex + 1}`}
                        </a>
                        {source.content && (
                          <p className="source-preview">
                            {source.content.length > SOURCE_LENGHT
                              ? source.content.slice(0, SOURCE_LENGHT) + '…'
                              : source.content
                            }
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* 2. Render the "pending" query (the one currently loading) */}
          {pendingQuery && (
            <div className="chat-item">
              <div className="question">
                {pendingQuery}
                <span className="timestamp">{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>
              
              {/* 3. Render the streaming answer */}
              {(response || loading) && (
                <div className="answer">
                  {loading && !response ? <span className="thinking-indicator"></span> : response}
                </div>
              )}
              
              {/* 4. Render the streaming sources */}
              {sources.length > 0 && (
                <div className="sources-section">
                  <h3 className="section-header-inline">Sources ({sources.length})</h3>
                  <div className="sources-list">
                    {sources.map((source, index) => (
                      <div key={index} className="source-item">
                        <a 
                          href={source.link || "#"} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="source-link"
                        >
                          {source.title || `Source ${index + 1}`}
                        </a>
                        {source.content && (
                          <p className="source-preview">
                            {source.content.length > SOURCE_LENGHT
                              ? source.content.slice(0, SOURCE_LENGHT) + '…'
                              : source.content
                            }
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* This is the input form at the bottom */}
        <form onSubmit={handleSubmit} className="query-form-bottom">
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
      </div>
    </div>
  );
}

export default App;