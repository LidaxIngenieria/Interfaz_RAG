from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables from .env file
load_dotenv()

# Import your existing RAG code
from model_interfaces.OpenAI_RAG import OpenAI_RAG
from chromadb import PersistentClient
from semantic_text_splitter import TextSplitter
from sentence_transformers import CrossEncoder

# Request/Response models
class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    query: str

# Initialize your RAG system
rag_system = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global rag_system
    CHUNK_SIZE = 1200
    CHUNK_OVERLAP = 200

    EMBED_MODEL_NAME = "text-embedding-3-small"
    LLM_NAME = "gpt-3.5-turbo" 

    TEXT_SPLITTER = TextSplitter.from_tiktoken_model("gpt-3.5-turbo", capacity=CHUNK_SIZE, overlap=CHUNK_OVERLAP)

    RERANKER = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    print("Initializing RAG system...")
    rag_system = OpenAI_RAG(EMBED_MODEL_NAME, LLM_NAME, TEXT_SPLITTER, RERANKER)
    print("RAG system initialized successfully!")
    
    yield
    # Shutdown - you can add cleanup code here if needed

# Create FastAPI app with lifespan
app = FastAPI(
    title="RAG API", 
    description="API for RAG Interface",
    lifespan=lifespan
)

# Add CORS middleware to allow React frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "RAG API is running"}

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    try:
        print(f"Received query: {request.query}")
        
        if rag_system is None:
            return {
                "answer": "RAG system is not initialized yet. Please try again in a moment.",
                "sources": [],
                "query": request.query
            }
        
        # Check if invoke_api method exists, otherwise use fallback
        if hasattr(rag_system, 'invoke_api'):
            response = rag_system.invoke_api(request.query)
        else:
            # Fallback if invoke_api method doesn't exist
            response = {
                "answer": f"Your RAG system is working! Query received: '{request.query}'. Note: The invoke_api method needs to be implemented in your OpenAI_Rag class.",
                "sources": [
                    {
                        "id": 1,
                        "title": "System Info",
                        "content": "RAG backend is connected but invoke_api method is missing",
                        "similarity": 0.9
                    }
                ],
                "query": request.query
            }
        
        return response
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health")
async def health_check():
    api_key_status = "configured" if os.getenv("OPENAI_API_KEY") else "missing"
    rag_status = "initialized" if rag_system else "not_initialized"
    
    return {
        "status": "healthy", 
        "openai_api_key": api_key_status,
        "rag_system": rag_status,
        "message": "Backend is running correctly"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)