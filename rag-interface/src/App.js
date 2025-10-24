import React, { useState, useEffect, useRef } from 'react';
import './App.css';
// Import your PNG image
import lidaxLogo from './Lidax_logo.svg'; 
import ReactMarkdown from 'react-markdown';

function App() {
    const BACKEND_URL = "http://192.168.1.163:8000";
    const SOURCE_LENGHT = 300;
    const [query, setQuery] = useState('');
    const [pendingQuery, setPendingQuery] = useState(''); 
    const [response, setResponse] = useState('');
    const [sources, setSources] = useState([]);
    const [images, setImages] = useState([]); // State for streaming images 🛑 CORRECTED
    const [loading, setLoading] = useState(false);
    const [chatHistory, setChatHistory] = useState([]);
    const chatFeedRef = useRef(null); 
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
    }, [chatHistory, response]); 


    // Streamed API call (One-Call JSONL approach)
    // 🛑 CORRECTED: Added onImage to function signature 🛑
    const callRagApiStream = async (question, onChunk, onFinal, onImage) => {
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
                        } else if (item.type === 'images') { // Handle images type
                            onImage(item.content);
                        } else if (item.type === 'error') {
                            throw new Error(item.message);
                        }
                    } catch (error) {
                        console.error("Failed to parse JSONL line:", error);
                    }
                }
            }
            
            // Handle remaining buffer (for final item)
            if (buffer.trim()) {
                try {
                    const item = JSON.parse(buffer.trim());
                    if (item.type === 'final') {
                        onFinal(item.sources);
                    } else if (item.type === 'images') {
                        onImage(item.content);
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
        setImages([]); // Clear images for new query
        setPendingQuery(currentQuery); 
        setQuery(""); 
        
        let streamedAnswer = "";
        let finalSources = [];
        let finalImages = []; // Accumulator for history object

        try {
            // Stream the answer and capture final data
            // 🛑 CORRECTED: Pass the fourth callback (onImage) 🛑
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
                },
                (imgRefs) => {
                    // Callback for image references
                    finalImages = imgRefs; // Accumulate for history
                    setImages(imgRefs);     // Set for streaming view
                }
            );

            // Add the COMPLETED exchange to history
            setChatHistory(prev => [
                ...prev,
                {
                    question: currentQuery,
                    answer: streamedAnswer,
                    sources: finalSources, 
                    images: finalImages, // Save final image list
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
                    images: [], // Include empty images array
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                }
            ]);
        } finally {
            // Clear the "pending" states
            setPendingQuery("");
            setResponse("");
            setSources([]);
            setImages([]); // Clear streaming image state
            setLoading(false);
        }
    };

    const clearChat = () => {
        setChatHistory([]);
        setPendingQuery('');
        setResponse('');
        setSources([]);
        setImages([]); // Clear streaming image state
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
                                {/*{chat.answer} */}
                                <ReactMarkdown>{chat.answer}</ReactMarkdown>
                            </div>

                            {/* Render IMAGES for completed chat item */}
                            {chat.images && chat.images.length > 0 && (
                                <div className="images-section">
                                    <h3 className="section-header-inline">References ({chat.images.length})</h3>
                                    <div className="image-list">
                                        {chat.images.map((imagePath, imgIndex) => (
                                            <img 
                                                key={imgIndex} 
                                                src={`${BACKEND_URL}/${imagePath}`} 
                                                alt={`Reference ${imgIndex + 1}`} 
                                                className="referenced-image"
                                            />
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Render SOURCES for completed chat item */}
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
                                    {loading && !response ? <span className="thinking-indicator"></span> : <ReactMarkdown>{response}</ReactMarkdown>}
                                </div>
                            )}
                            
                            {/* Render IMAGES for streaming chat item */}
                            {images.length > 0 && (
                                <div className="images-section">
                                    <h3 className="section-header-inline">References ({images.length})</h3>
                                    <div className="image-list">
                                        {images.map((imagePath, imgIndex) => (
                                            <img 
                                                key={imgIndex} 
                                                src={`${BACKEND_URL}/${imagePath}`} 
                                                alt={`Reference ${imgIndex + 1}`} 
                                                className="referenced-image"
                                            />
                                        ))}
                                    </div>
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