from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from utils.llm_utils import extract_entities, decision_prompt

# Load embeddings model (same as in ingest.py)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def process_query(query_text):
    # Load FAISS vectorstore with same embedding model
    db = FAISS.load_local("vectorstore/faiss_index", embeddings)

    # Optional: extract structured info (age, gender, etc.)
    entities = extract_entities(query_text)  # can use or ignore based on use

    # Embed query using same HuggingFace model
    query_embedding = embeddings.embed_query(query_text)

    # Perform semantic search
    retrieved_docs = db.similarity_search_by_vector(query_embedding, k=5)

    # Generate decision using language model (still GPT-based via llm_utils)
    decision = decision_prompt(query_text, retrieved_docs)
    return decision
