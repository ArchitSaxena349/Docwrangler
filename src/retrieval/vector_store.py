import logging
from typing import List, Dict, Any, Optional
from core.models import DocumentChunk, RetrievalResult
from core.config import Config

logger = logging.getLogger(__name__)

# Conditional imports for heavy dependencies
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    HEAVY_DEPS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Heavy dependencies not found: {e}. Running in lightweight mode.")
    HEAVY_DEPS_AVAILABLE = False

class VectorStore:
    """Vector database for document storage and retrieval"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_model = None
        
    def _ensure_initialized(self):
        """Lazy initialize resources"""
        if not HEAVY_DEPS_AVAILABLE:
            return

        if self.client is None:
            logger.info("Initializing ChromaDB client...")
            self.client = chromadb.PersistentClient(
                path=Config.CHROMA_PERSIST_DIRECTORY,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=Config.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            
        if self.embedding_model is None:
            logger.info(f"Loading embedding model: {Config.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
    
    def add_documents(self, chunks: List[DocumentChunk]) -> None:
        """Add document chunks to vector store"""
        if not HEAVY_DEPS_AVAILABLE:
            logger.warning("add_documents ignored in lightweight mode")
            return

        if not chunks:
            return
            
        self._ensure_initialized()
        
        # Generate embeddings
        texts = [chunk.content for chunk in chunks]
        embeddings = self._generate_embeddings(texts)
        
        # Prepare data for ChromaDB
        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = []
        
        for chunk in chunks:
            metadata = chunk.metadata.copy()
            metadata['document_id'] = chunk.document_id
            metadatas.append(metadata)
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
    
    def search(self, query: str, top_k: int = None, 
               document_ids: Optional[List[str]] = None) -> List[RetrievalResult]:
        """Search for relevant documents"""
        if not HEAVY_DEPS_AVAILABLE:
            logger.warning("search ignored in lightweight mode")
            return []

        self._ensure_initialized()

        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self._generate_embeddings([query])[0]
        
        # Prepare where clause for filtering
        where_clause = None
        if document_ids:
            where_clause = {"document_id": {"$in": document_ids}}
        
        # Search in vector store
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Convert to RetrievalResult objects
        retrieval_results = []
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                similarity_score = 1 - results['distances'][0][i]  # Convert distance to similarity
                
                if similarity_score >= Config.SIMILARITY_THRESHOLD:
                    result = RetrievalResult(
                        chunk_id=results['ids'][0][i],
                        document_id=results['metadatas'][0][i]['document_id'],
                        content=results['documents'][0][i],
                        similarity_score=similarity_score,
                        metadata=results['metadatas'][0][i]
                    )
                    retrieval_results.append(result)
        
        return retrieval_results
    
    def delete_document(self, document_id: str) -> None:
        """Delete all chunks for a document"""
        if not HEAVY_DEPS_AVAILABLE:
            logger.warning("delete_document ignored in lightweight mode")
            return

        self._ensure_initialized()
        self.collection.delete(where={"document_id": document_id})
    
    def get_document_count(self) -> int:
        """Get total number of documents in store"""
        if not HEAVY_DEPS_AVAILABLE:
            return 0
            
        self._ensure_initialized()
        return self.collection.count()
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model"""
        if not HEAVY_DEPS_AVAILABLE:
            return [[0.0] * 384] * len(texts) # Mock embedding

        self._ensure_initialized()
        try:
            embeddings = self.embedding_model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    def list_documents(self) -> List[str]:
        """List all document IDs in the store"""
        if not HEAVY_DEPS_AVAILABLE:
            return []

        self._ensure_initialized()
        results = self.collection.get(include=['metadatas'])
        document_ids = set()
        if results['metadatas']:
            for metadata in results['metadatas']:
                document_ids.add(metadata['document_id'])
        return list(document_ids)