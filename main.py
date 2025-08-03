from fastapi import FastAPI, Body, HTTPException
from query import process_query
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="LLM Document Wrangler",
    description="AI-powered insurance policy document analysis API",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "LLM Document Wrangler API", "status": "running"}

@app.post("/analyze")
def analyze(query: str = Body(..., embed=True)):
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        result = process_query(query)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "LLM Document Wrangler"}
