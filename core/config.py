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
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile") # Updated to replace decommissioned llama3-70b-8192

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
    SIMILARITY_THRESHOLD = 0.1 # Lowered from 0.3 to ensure retrieval of policy documents

    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8001"))

    # File uploads
    UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY", "uploads")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB


# Backwards-compatible alias
VECTOR_STORE_PATH = Config.CHROMA_PERSIST_DIRECTORY