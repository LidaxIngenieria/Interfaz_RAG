// // App.js

// import React, { useState, useEffect, useRef } from 'react';
// import './App.css';

// function App() {
//   const [query, setQuery] = useState('');
//   const [response, setResponse] = useState('');
//   const [sources, setSources] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [chatHistory, setChatHistory] = useState([]);
//   const historyContentRef = useRef(null);
//   const [darkMode, setDarkMode] = useState(false);

//   // Load saved theme preference
//   useEffect(() => {
//     const savedMode = localStorage.getItem("darkMode") === "true";
//     setDarkMode(savedMode);
//   }, []);

//   // Apply dark mode class + save preference
//   useEffect(() => {
//     document.body.classList.toggle("dark-mode", darkMode);
//     localStorage.setItem("darkMode", darkMode);
//   }, [darkMode]);

//   useEffect(() => {
//     if (historyContentRef.current) {
//       historyContentRef.current.scrollTop = historyContentRef.current.scrollHeight;
//     }
//   }, [chatHistory]);

//   const callRagApi = async (question) => {
//     try {
//       const apiResponse = await fetch('http://localhost:8000/query', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ query: question }),
//       });
      
//       if (!apiResponse.ok) {
//         const errorData = await apiResponse.json();
//         throw new Error(errorData.detail || 'API request failed');
//       }
      
//       return await apiResponse.json();

//     } catch (error) {
//       console.error('API call failed:', error);
//       return {
//         answer: `This is a mock response because the API call failed. Error: ${error.message}.`,
//         sources: [
//           { 
//             id: 1,
//             title: 'mock_document.pdf', 
//             link: '#',
//             content: 'This is example preview text from a source document used as fallback.'
//           }
//         ],
//         query: question
//       };
//     }
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (!query.trim()) return;

//     setLoading(true);
//     setResponse('');
//     setSources([]);
    
//     try {
//       const result = await callRagApi(query);
      
//       setResponse(result.answer);
//       setSources(result.sources || []);
      
//       setChatHistory(prev => [...prev, {
//         question: query,
//         answer: result.answer,
//         timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
//       }]);
      
//       setQuery('');

//     } catch (error) {
//       console.error('Error:', error);
//       setResponse(`Sorry, there was an error processing your request: ${error.message}`);
    
//     } finally {
//       setLoading(false);
//     }
//   };

//   const clearChat = () => {
//     setChatHistory([]);
//     setResponse('');
//     setSources([]);
//   };

//   return (
//     <div className="app">
//       <header className="app-header">
//         <h1>Lidax Interface</h1>
//         <button 
//           className="theme-toggle" 
//           onClick={() => setDarkMode(!darkMode)} 
//           aria-label="Toggle dark mode"
//         >
//           {darkMode ? '☀️' : '🌙'}
//         </button>
//       </header>

//       <div className="app-container">
//         {/* Chat History */}
//         <div className="chat-history card">
//           <div className="history-header">
//             <h3>Conversation</h3>
//             <button onClick={clearChat} className="clear-btn">
//               Clear
//             </button>
//           </div>
//           <div className="history-content" ref={historyContentRef}>
//             {chatHistory.length === 0 ? (
//               <p className="empty-state">Your conversation will appear here.</p>
//             ) : (
//               chatHistory.map((chat, index) => (
//                 <div key={index} className="chat-item">
//                   <div className="question">
//                     {chat.question}
//                     <span className="timestamp">{chat.timestamp}</span>
//                   </div>
//                   <div className="answer history-answer-preview">
//                     {chat.answer}
//                   </div>
//                 </div>
//               ))
//             )}
//           </div>
//         </div>

//         {/* Main Content */}
//         <div className="main-content">
//           <form onSubmit={handleSubmit} className="query-form card">
//             <div className="input-group">
//               <input
//                 type="text"
//                 value={query}
//                 onChange={(e) => setQuery(e.target.value)}
//                 placeholder="Ask a question..."
//                 disabled={loading}
//                 className="query-input"
//               />
//               <button 
//                 type="submit" 
//                 disabled={loading || !query.trim()}
//                 className="submit-btn"
//               >
//                 {loading ? 'Thinking...' : 'Ask'}
//               </button>
//             </div>
//           </form>

//           {(response || loading) && (
//             <div className="response-container">
//               <div className="response-section card">
//                 <h3 className="section-header">Answer</h3>
//                 <div className="response-content">
//                   {loading && !response ? "Generating answer..." : response}
//                 </div>
//               </div>
              
//               {sources.length > 0 && (
//                 <div className="sources-section card" style={{marginTop: '2rem'}}>
//                   <h3 className="section-header">Sources ({sources.length})</h3>
//                   <div className="sources-list">
//                     {sources.map((source) => (
//                       <div key={source.id} className="source-item">
//                         <a 
//                           href={source.link || "#"} 
//                           target="_blank" 
//                           rel="noopener noreferrer" 
//                           className="source-link"
//                         >
//                           {source.title}
//                         </a>
//                         {source.content && (
//                           <p className="source-preview">
//                             {source.content.length > 150
//                               ? source.content.slice(0, 150) + '…'
//                               : source.content
//                             }
//                           </p>
//                         )}
//                       </div>
//                     ))}
//                   </div>
//                 </div>
//               )}
//             </div>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

// export default App;

// App.js
import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const historyContentRef = useRef(null);
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

  // Auto-scroll chat history
  useEffect(() => {
    if (historyContentRef.current) {
      historyContentRef.current.scrollTop = historyContentRef.current.scrollHeight;
    }
  }, [chatHistory]);


  // Streamed API call (One-Call JSONL approach)
  const callRagApiStream = async (question, onChunk, onFinal) => {
    try {
      console.log("Starting stream request (JSONL)...");
      const response = await fetch("http://localhost:8000/query/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: question }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = ''; // Buffer to hold incomplete JSON lines
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log("Stream completed.");
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        // Process line-by-line, as the server yields JSON objects followed by '\n'
        let lines = buffer.split('\n');
        buffer = lines.pop(); // Keep the potentially incomplete last line in the buffer

        for (const line of lines) {
            if (!line.trim()) continue;
            try {
                const item = JSON.parse(line);

                if (item.type === 'chunk') {
                    // 1. Handle Text Chunk
                    onChunk(item.content);
                } else if (item.type === 'final') {
                    // 2. Handle Final Metadata (Sources)
                    onFinal(item.sources);
                } else if (item.type === 'error') {
                    throw new Error(item.message);
                }
            } catch (error) {
                console.error("Failed to parse JSONL line:", error);
            }
        }
      }
      
      // Attempt to process any remaining buffer after stream closure
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
    setQuery(""); 
    
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

      console.log("", streamedAnswer);

      // Update Chat History with the complete exchange
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
      setResponse(`Sorry, there was an error processing your request: ${error.message}`);
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
        <h1>Lidax Interface</h1>
        <button 
          className="theme-toggle" 
          onClick={() => setDarkMode(!darkMode)} 
          aria-label="Toggle dark mode"
        >
          {darkMode ? '☀️' : '🌙'}
        </button>
      </header>

      <div className="app-container">
        {/* Chat History */}
        <div className="chat-history card">
          <div className="history-header">
            <h3>Conversation History</h3>
            <button onClick={clearChat} className="clear-btn">Clear</button>
          </div>
          <div className="history-content" ref={historyContentRef}>
            {chatHistory.length === 0 ? (
              <p className="empty-state">Your conversation will appear here.</p>
            ) : (
              chatHistory.map((chat, index) => (
                <div key={index} className="chat-item">
                  <div className="question">
                    {chat.question}
                    <span className="timestamp">{chat.timestamp}</span>
                  </div>
                  <div className="answer history-answer-preview">
                    {chat.answer}
                  </div>
                  {/* Optional: Display sources in history preview */}
                  {chat.sources && chat.sources.length > 0 && (
                      <span className="source-count">({chat.sources.length} sources)</span>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="main-content">
          <form onSubmit={handleSubmit} className="query-form card">
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

          {(response || loading) && (
            <div className="response-container">
              <div className="response-section card">
                <h3 className="section-header">Answer</h3>
                <div className="response-content">
                  {loading && !response ? "Generating answer..." : response}
                </div>
              </div>
              
              {/* Sources Section */}
              {sources.length > 0 && (
                <div className="sources-section card" style={{marginTop: '2rem'}}>
                  <h3 className="section-header">Sources ({sources.length})</h3>
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
                            {source.content.length > 150
                              ? source.content.slice(0, 150) + '…'
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
      </div>
    </div>
  );
}

export default App;