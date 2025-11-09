from typing import List, Dict, Any
from openai import OpenAI
from core.models import ParsedQuery, RetrievalResult, DecisionResult
from core.config import Config
import json

class DecisionEvaluator:
    """Evaluate queries against retrieved documents to make decisions"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def evaluate(self, parsed_query: ParsedQuery, 
                retrieved_docs: List[RetrievalResult]) -> DecisionResult:
        """Evaluate query against retrieved documents"""
        
        if not retrieved_docs:
            return DecisionResult(
                decision="insufficient_information",
                justification="No relevant documents found to make a decision",
                source_clauses=[],
                confidence_score=0.0
            )
        
        # Prepare context for LLM
        context = self._prepare_context(retrieved_docs)
        
        # Generate decision using LLM
        decision_prompt = self._create_decision_prompt(parsed_query, context)
        
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": decision_prompt}
                ],
                temperature=0.1
            )
            
            # Parse LLM response
            decision_data = json.loads(response.choices[0].message.content)
            
            return DecisionResult(
                decision=decision_data.get("decision", "pending"),
                amount=decision_data.get("amount"),
                justification=decision_data.get("justification", ""),
                source_clauses=decision_data.get("source_clauses", []),
                confidence_score=decision_data.get("confidence_score", 0.5),
                metadata=decision_data.get("metadata", {})
            )
            
        except Exception as e:
            return DecisionResult(
                decision="error",
                justification=f"Error in decision evaluation: {str(e)}",
                source_clauses=[],
                confidence_score=0.0
            )
    
    def _prepare_context(self, retrieved_docs: List[RetrievalResult]) -> str:
        """Prepare context from retrieved documents"""
        context = "RELEVANT DOCUMENT SECTIONS:\n\n"
        
        for i, doc in enumerate(retrieved_docs, 1):
            context += f"Section {i} (Document: {doc.document_id}, Similarity: {doc.similarity_score:.3f}):\n"
            context += f"{doc.content}\n"
            context += f"Metadata: {doc.metadata}\n\n"
        
        return context
    
    def _create_decision_prompt(self, parsed_query: ParsedQuery, context: str) -> str:
        """Create decision prompt for LLM"""
        return f"""
        QUERY ANALYSIS:
        Original Query: {parsed_query.original_query}
        Structured Data: {json.dumps(parsed_query.structured_data, indent=2)}
        Query Type: {parsed_query.query_type}
        Intent: {parsed_query.intent}
        Key Entities: {parsed_query.key_entities}
        
        {context}
        
        Based on the query and the relevant document sections above, make a decision and provide your response in the following JSON format:
        
        {{
            "decision": "approved|rejected|pending|insufficient_information",
            "amount": null or numeric value if applicable,
            "justification": "Clear explanation of the decision with specific references to document sections",
            "source_clauses": ["list", "of", "specific", "clause", "identifiers", "or", "section", "references"],
            "confidence_score": 0.0 to 1.0,
            "metadata": {{
                "reasoning_steps": ["step1", "step2", "step3"],
                "key_factors": ["factor1", "factor2"],
                "potential_issues": ["issue1", "issue2"] or null
            }}
        }}
        
        Guidelines:
        1. Base your decision strictly on the provided document sections
        2. Reference specific clauses or sections in your justification
        3. If information is insufficient, state what additional information is needed
        4. Provide a confidence score based on how well the documents address the query
        5. Include reasoning steps in metadata for transparency
        """
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for decision making"""
        return """
        You are an expert document analyst specializing in policy interpretation, contract analysis, and decision making based on document content.
        
        Your role is to:
        1. Analyze queries against provided document sections
        2. Make accurate decisions based on document content
        3. Provide clear justifications with specific references
        4. Identify when information is insufficient for a decision
        5. Maintain consistency in decision-making logic
        
        Key principles:
        - Be precise and factual
        - Reference specific document sections
        - Explain your reasoning clearly
        - Acknowledge limitations and uncertainties
        - Provide actionable insights
        
        Always respond with valid JSON in the specified format.
        """