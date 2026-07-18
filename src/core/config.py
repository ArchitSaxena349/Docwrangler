import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration.

    Values are read from environment variables where possible. The default
    CHROMA persist directory is set to the centralized `data/vector_store/...`
    location used by the example scripts.
    """

    # Gemini / LLM
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Groq / LLM
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  # Updated to replace decommissioned llama3-70b-8192
    GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "llama-3.2-11b-vision-preview")

    # Vector DB
    CHROMA_PERSIST_DIRECTORY = os.getenv(
        "CHROMA_PERSIST_DIRECTORY",
        os.path.join("data", "vector_store", "local_chroma_db"),
    )
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "insurance_docs")

    # Document processing / retrieval
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
    # Fix #2: Read from env var; default 0.3 is a sensible middle ground
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))

    # API — Fix #3: default to 8000 to match uvicorn convention
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # File uploads
    UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY", "uploads")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB

    # CORS
    ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin.strip()]


# Backwards-compatible alias
VECTOR_STORE_PATH = Config.CHROMA_PERSIST_DIRECTORY
