import asyncio
from typing import List
from src.core.models import QueryRequest, ProcessingResponse, RetrievalResult
from src.query_engine.parser import QueryParser
from src.retrieval.vector_store import VectorStore
from src.retrieval.hybrid_search import HybridSearcher
from src.decision_engine.evaluator import DecisionEvaluator

class QueryService:
    """Service for processing natural language queries"""
    
    def __init__(self):
        self.query_parser = QueryParser()
        self.vector_store = VectorStore()
        self.hybrid_searcher = HybridSearcher(self.vector_store)
        self.decision_evaluator = DecisionEvaluator()
    
    async def process_query(self, request: QueryRequest) -> ProcessingResponse:
        """Process a complete query request"""
        try:
            # Parse the query using thread pool to avoid blocking event loop
            parsed_query = await asyncio.to_thread(self.query_parser.parse_query, request.query)
            
            # Retrieve relevant documents
            retrieved_docs = await asyncio.to_thread(
                self.hybrid_searcher.search,
                query=request.query,
                document_ids=request.document_ids
            )
            
            # Make decision based on retrieved documents
            decision = await asyncio.to_thread(
                self.decision_evaluator.evaluate, 
                parsed_query, 
                retrieved_docs, 
                request.context
            )
            
            return ProcessingResponse(
                query=request.query,
                parsed_query=parsed_query,
                retrieved_documents=retrieved_docs,
                decision=decision,
                processing_time=0.0  # Will be set by the API route
            )
            
        except Exception as e:
            raise Exception(f"Error processing query: {str(e)}") from e
    
    def search_documents(self, query: str, top_k: int = 5, 
                        document_ids: List[str] = None) -> List[RetrievalResult]:
        """Search for relevant documents"""
        try:
            return self.hybrid_searcher.search(
                query=query,
                top_k=top_k,
                document_ids=document_ids
            )
        except Exception as e:
            raise Exception(f"Error searching documents: {str(e)}") from e