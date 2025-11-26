from typing import List, Dict, Any
import google.generativeai as genai
from core.models import ParsedQuery, RetrievalResult, DecisionResult
from core.config import Config
import json

class DecisionEvaluator:
    """Evaluate queries against retrieved documents to make decisions"""
    
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
    
    def evaluate(self, parsed_query: ParsedQuery, 
                retrieved_docs: List[RetrievalResult]) -> DecisionResult:
        """Evaluate query against retrieved documents"""
        
        if not retrieved_docs:
            return DecisionResult(
                decision="insufficient_information",
                payment_mode="unknown",
                justification="No relevant documents found to make a decision",
                source_clauses=[],
                confidence_score=0.0
            )
        
        # Prepare context for LLM
        context = self._prepare_context(retrieved_docs)
        
        # Generate decision using LLM
        decision_prompt = self._create_decision_prompt(parsed_query, context)
        
        try:
            # Combine system prompt and user prompt for Gemini
            full_prompt = f"{self._get_system_prompt()}\n\n{decision_prompt}"
            response = self.model.generate_content(full_prompt)
            
            # Parse response - extract JSON
            text = response.text
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                decision_data = json.loads(text[json_start:json_end])
            else:
                decision_data = {}
            
            return DecisionResult(
                decision=decision_data.get("decision", "pending"),
                payment_mode=decision_data.get("payment_mode", "unknown"),
                amount=decision_data.get("amount"),
                justification=decision_data.get("justification", ""),
                source_clauses=decision_data.get("source_clauses", []),
                confidence_score=decision_data.get("confidence_score", 0.5),
                metadata=decision_data.get("metadata", {})
            )
            
        except Exception as e:
            return DecisionResult(
                decision="error",
                payment_mode="unknown",
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
        
        {context}
        
        Based on the query and the relevant document sections above, make a decision and provide your response in the following JSON format:
        
        {{
            "decision": "approved|rejected|pending|insufficient_information",
            "payment_mode": "cashless|reimbursement|unknown",
            "amount": null or numeric value if applicable (calculate based on coverage limits, deductibles, and co-pay),
            "justification": "Clear explanation of the decision. Explicitly state why it is Cashless or Reimbursement (e.g., 'Hospital is in-network'). Detail the amount calculation.",
            "source_clauses": ["list", "of", "specific", "clause", "identifiers", "or", "section", "references"],
            "confidence_score": 0.0 to 1.0,
            "metadata": {{
                "reasoning_steps": ["step1", "step2", "step3"],
                "key_factors": ["factor1", "factor2"],
                "potential_issues": ["issue1", "issue2"] or null
            }}
        }}
        
        Guidelines:
        1. Base your decision strictly on the provided document sections.
        2. **Payment Mode**: Check if the hospital/provider is mentioned in the query. If it matches a "Network Hospital" list in the documents, set to "cashless". Otherwise, "reimbursement".
        3. **Amount Calculation**: Apply deductibles and co-pays to the claimed amount.
        4. Reference specific clauses or sections in your justification.
        5. If information is insufficient, state what additional information is needed.
        6. Provide a confidence score based on how well the documents address the query.
        7. Include reasoning steps in metadata for transparency.
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