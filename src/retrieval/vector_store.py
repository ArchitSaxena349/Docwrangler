import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from openai import OpenAI
from core.models import DocumentChunk, RetrievalResult
from core.config import Config

class VectorStore:
    """Vector database for document storage and retrieval"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=Config.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=Config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def add_documents(self, chunks: List[DocumentChunk]) -> None:
        """Add document chunks to vector store"""
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
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
    
    def search(self, query: str, top_k: int = None, 
               document_ids: Optional[List[str]] = None) -> List[RetrievalResult]:
        """Search for relevant documents"""
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
        self.collection.delete(where={"document_id": document_id})
    
    def get_document_count(self) -> int:
        """Get total number of documents in store"""
        return self.collection.count()
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model=Config.EMBEDDING_MODEL,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    def list_documents(self) -> List[str]:
        """List all document IDs in the store"""
        results = self.collection.get(include=['metadatas'])
        document_ids = set()
        for metadata in results['metadatas']:
            document_ids.add(metadata['document_id'])
        return list(document_ids)