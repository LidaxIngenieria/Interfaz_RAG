# main.py - Fixed streaming version
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Iterator
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.responses import StreamingResponse
import json
import asyncio

# Load environment variables from .env file
load_dotenv()

# Import your existing RAG code
from model_interfaces import Chroma_RAG, LLM, E_Model, Image_Model
from semantic_text_splitter import TextSplitter
from sentence_transformers import CrossEncoder

# --- Simplified request/response models ---
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    query: str

# Initialize your RAG system
rag_system = None

# Lifespan startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_system
    CHUNK_SIZE = 1200
    CHUNK_OVERLAP = 200
    TEXT_MODEL = LLM.Ollama_LLM("react-mistral")
    EMBED_MODEL = E_Model.Ollama_Embedding("nomic-embed-text")
    IMAGE_MODEL = Image_Model.Image_Model("NOne")

    TEXT_SPLITTER = TextSplitter.from_tiktoken_model(
        "gpt-3.5-turbo", capacity=CHUNK_SIZE, overlap=CHUNK_OVERLAP
    )
    RERANKER = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    print("Initializing RAG system...")
    rag_system = Chroma_RAG.Chroma_RAG(EMBED_MODEL, TEXT_MODEL, IMAGE_MODEL, TEXT_SPLITTER, RERANKER)
    print("RAG system initialized successfully!")

    yield
    # Shutdown (if needed)

# Create FastAPI app
app = FastAPI(
    title="Lidax RAG API",
    description="API for the Lidax RAG Interface",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*" ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Lidax RAG API is running"}

# --- Standard query endpoint ---
@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    try:
        if rag_system is None:
            raise HTTPException(status_code=503, detail="RAG system not initialized.")

        response = rag_system.invoke_api(request.query)
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# In main.py
@app.post("/query/stream")
async def query_rag_stream(request: QueryRequest):
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized.")

    def generate_stream():
        try:
            # rag_system.invoke_as_stream yields Python dicts: {"type": "chunk", "content": "..."} or {"type": "final", "sources": [...]}
            stream = rag_system.invoke_as_stream(request.query)
            
            for item in stream:
                # 🛑 CRITICAL FIX: Explicitly serialize the Python dictionary to a JSON line 🛑
                # This ensures the client receives a clean JSON string, not a Python dict's __repr__
                yield json.dumps(item) + "\n"
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Send an error payload as the final item in the stream
            error_payload = {"type": "error", "message": f"Error during streaming: {str(e)}"}
            yield json.dumps(error_payload) + "\n"

    return StreamingResponse(
        generate_stream(),
        # Use text/plain for maximum compatibility, even though it's JSONL
        media_type="text/plain"
    )


# --- Health check ---
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

# --- Run server ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)