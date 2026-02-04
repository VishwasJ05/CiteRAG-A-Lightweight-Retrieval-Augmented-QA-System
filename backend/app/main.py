"""FastAPI Main Application"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routers import ingest, query

# Load environment variables from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(
    title="Mini RAG API",
    description="A small RAG application with retrieval, reranking, and LLM answering",
    version="0.1.0"
)

# CORS configuration - will be updated with specific origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router)
app.include_router(query.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Mini RAG API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "mini-rag-api",
        "version": "0.1.0"
    }
