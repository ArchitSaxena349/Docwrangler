from typing import List
from core.models import QueryRequest, ProcessingResponse, RetrievalResult
from query_engine.parser import QueryParser
from retrieval.vector_store import VectorStore
from decision_engine.evaluator import DecisionEvaluator

class QueryService:
    """Service for processing natural language queries"""
    
    def __init__(self):
        self.query_parser = QueryParser()
        self.vector_store = VectorStore()
        self.decision_evaluator = DecisionEvaluator()
    
    async def process_query(self, request: QueryRequest) -> ProcessingResponse:
        """Process a complete query request"""
        try:
            # Parse the query
            parsed_query = self.query_parser.parse_query(request.query)
            
            # Retrieve relevant documents
            retrieved_docs = self.vector_store.search(
                query=request.query,
                document_ids=request.document_ids
            )
            
            # Make decision based on retrieved documents
            decision = self.decision_evaluator.evaluate(parsed_query, retrieved_docs)
            
            return ProcessingResponse(
                query=request.query,
                parsed_query=parsed_query,
                retrieved_documents=retrieved_docs,
                decision=decision,
                processing_time=0.0  # Will be set by the API route
            )
            
        except Exception as e:
            raise Exception(f"Error processing query: {str(e)}")
    
    def search_documents(self, query: str, top_k: int = 5, 
                        document_ids: List[str] = None) -> List[RetrievalResult]:
        """Search for relevant documents"""
        try:
            return self.vector_store.search(
                query=query,
                top_k=top_k,
                document_ids=document_ids
            )
        except Exception as e:
            raise Exception(f"Error searching documents: {str(e)}")