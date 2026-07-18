import logging
import re
from typing import List, Dict, Any, Optional
from src.core.models import RetrievalResult, DocumentChunk
from src.core.config import Config
from src.retrieval.vector_store import VectorStore

logger = logging.getLogger(__name__)

class HybridSearcher:
    """Hybrid Search combining ChromaDB vector search and BM25 lexical search using Reciprocal Rank Fusion (RRF)"""
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store or VectorStore()
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer for BM25 indexing"""
        return re.findall(r'\w+', text.lower())
        
    def search(self, query: str, top_k: Optional[int] = None, 
               document_ids: Optional[List[str]] = None) -> List[RetrievalResult]:
        """Perform hybrid search and merge using RRF"""
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
            
        self.vector_store._ensure_initialized()
        
        # If heavy dependencies are missing or we are in mock mode, return standard vector store output
        from src.retrieval.vector_store import HEAVY_DEPS_AVAILABLE
        if not HEAVY_DEPS_AVAILABLE or self.vector_store.collection is None:
            logger.warning("Heavy dependencies missing or vector store not initialized. Falling back to vector store search.")
            return self.vector_store.search(query, top_k, document_ids)
            
        try:
            # 1. Fetch dense vector results
            vector_results = self.vector_store.search(query, top_k=top_k * 2, document_ids=document_ids)
        except Exception as e:
            logger.error(f"Vector search failed: {e}", exc_info=True)
            vector_results = []
            
        try:
            # 2. Fetch BM25 lexical results
            bm25_results = self._bm25_search(query, top_k=top_k * 2, document_ids=document_ids)
        except Exception as e:
            logger.error(f"BM25 lexical search failed: {e}", exc_info=True)
            bm25_results = []
            
        # 3. Apply Reciprocal Rank Fusion (RRF)
        return self._reciprocal_rank_fusion(vector_results, bm25_results, top_k)
        
    def _bm25_search(self, query: str, top_k: int, 
                    document_ids: Optional[List[str]] = None) -> List[RetrievalResult]:
        """Perform BM25 search over documents in ChromaDB"""
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            logger.warning("rank_bm25 library not available. Skipping lexical search.")
            return []
            
        # Build where clause for filtering
        where_clause = None
        if document_ids:
            if len(document_ids) == 1:
                where_clause = {"document_id": document_ids[0]}
            else:
                where_clause = {"document_id": {"$in": document_ids}}
                
        # Get all matching chunks from ChromaDB
        results = self.vector_store.collection.get(
            where=where_clause,
            include=['documents', 'metadatas']
        )
        
        if not results or not results['documents']:
            return []
            
        documents = results['documents']
        metadatas = results['metadatas']
        ids = results['ids']
        
        # Tokenize corpus
        tokenized_corpus = [self._tokenize(doc) for doc in documents]
        bm25 = BM25Okapi(tokenized_corpus)
        
        # Score documents
        tokenized_query = self._tokenize(query)
        scores = bm25.get_scores(tokenized_query)
        
        # Sort and get top results
        scored_docs = []
        for idx, score in enumerate(scores):
            if score > 0:  # Only keep documents with some keyword overlap
                scored_docs.append((score, idx))
                
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        top_scored = scored_docs[:top_k]
        
        # Convert to RetrievalResult objects
        # Normalize scores to pseudo-similarity values between 0 and 1
        max_score = max([s[0] for s in top_scored]) if top_scored else 1.0
        
        retrieval_results = []
        for score, idx in top_scored:
            norm_score = score / max_score if max_score > 0 else 0.0
            # Normalize to match similarity threshold if needed
            result = RetrievalResult(
                chunk_id=ids[idx],
                document_id=metadatas[idx]['document_id'],
                content=documents[idx],
                similarity_score=norm_score,
                metadata=metadatas[idx]
            )
            retrieval_results.append(result)
            
        return retrieval_results
        
    def _reciprocal_rank_fusion(self, vector_results: List[RetrievalResult], 
                               bm25_results: List[RetrievalResult], 
                               top_k: int, constant: int = 60) -> List[RetrievalResult]:
        """Merge rankings using Reciprocal Rank Fusion (RRF)"""
        rrf_scores = {}
        doc_map = {}
        
        # Rank dense vector results
        for rank, doc in enumerate(vector_results, 1):
            doc_id = doc.chunk_id
            doc_map[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (constant + rank))
            
        # Rank BM25 results
        for rank, doc in enumerate(bm25_results, 1):
            doc_id = doc.chunk_id
            if doc_id not in doc_map:
                doc_map[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (constant + rank))
            
        # Sort by RRF score
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Build final unified list
        final_results = []
        for doc_id, rrf_score in sorted_docs[:top_k]:
            doc = doc_map[doc_id]
            # Add RRF metadata for auditability
            doc.metadata['rrf_score'] = rrf_score
            final_results.append(doc)
            
        return final_results
