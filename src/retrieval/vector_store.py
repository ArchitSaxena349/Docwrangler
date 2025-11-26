import logging
from typing import List, Dict, Any, Optional
from core.models import DocumentChunk, RetrievalResult
from core.config import Config

logger = logging.getLogger(__name__)

# Global flag, will be updated in _ensure_initialized
HEAVY_DEPS_AVAILABLE = True

class VectorStore:
    """Vector database for document storage and retrieval"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._heavy_deps_checked = False
        
    def _ensure_initialized(self):
        """Lazy initialize resources"""
        global HEAVY_DEPS_AVAILABLE
        
        if not self._heavy_deps_checked:
            try:
                global chromadb, Settings, SentenceTransformer
                import chromadb
                from chromadb.config import Settings
                from sentence_transformers import SentenceTransformer
                HEAVY_DEPS_AVAILABLE = True
            except ImportError as e:
                logger.warning(f"Heavy dependencies not found: {e}. Running in lightweight mode.")
                HEAVY_DEPS_AVAILABLE = False
            
            logger.info(f"VectorStore initialized. HEAVY_DEPS_AVAILABLE: {HEAVY_DEPS_AVAILABLE}")
            self._heavy_deps_checked = True

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
        self._ensure_initialized()
        
        if not HEAVY_DEPS_AVAILABLE:
            logger.warning("add_documents ignored in lightweight mode")
            return

        if not chunks:
            return
        
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
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            logger.info(f"Successfully added {len(ids)} chunks to ChromaDB. Collection count: {self.collection.count()}")
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")
            raise
    
    def search(self, query: str, top_k: int = None, 
               document_ids: Optional[List[str]] = None) -> List[RetrievalResult]:
        """Search for relevant documents"""
        self._ensure_initialized()
        
        if not HEAVY_DEPS_AVAILABLE:
            logger.warning("search ignored in lightweight mode")
            return []

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
        
        logger.info(f"Search Results: {results}")

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
        self._ensure_initialized()
        
        if not HEAVY_DEPS_AVAILABLE:
            logger.warning("delete_document ignored in lightweight mode")
            return

        self.collection.delete(where={"document_id": document_id})
    
    def get_document_count(self) -> int:
        """Get total number of documents in store"""
        self._ensure_initialized()
        
        if not HEAVY_DEPS_AVAILABLE:
            return 0
            
        return self.collection.count()
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model"""
        # _ensure_initialized is called by public methods
        if not HEAVY_DEPS_AVAILABLE:
            return [[0.0] * 384] * len(texts) # Mock embedding

        try:
            embeddings = self.embedding_model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    def list_documents(self) -> List[str]:
        """List all document IDs in the store"""
        self._ensure_initialized()
        
        if not HEAVY_DEPS_AVAILABLE:
            return []

        results = self.collection.get(include=['metadatas'])
        document_ids = set()
        if results['metadatas']:
            for metadata in results['metadatas']:
                document_ids.add(metadata['document_id'])
        return list(document_ids)