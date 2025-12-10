from typing import List, Dict, Any
from groq import Groq
from core.models import ParsedQuery, RetrievalResult, DecisionResult
from core.config import Config
import json

class DecisionEvaluator:
    """Evaluate queries against retrieved documents to make decisions"""
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
    
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
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": decision_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            text = response.choices[0].message.content
            decision_data = json.loads(text)
            
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
        1. **Step-by-Step Analysis**:
           a. Identify the specific medical procedure or query intent.
           b. Scan retrieved sections for keywords (inclusions, exclusions, waiting periods).
           c. Check if the provider/location affects coverage (Network vs Non-network).
           d. Calculate payable amount only if coverage is confirmed.
        
        2. **Decision Logic**:
           - **Approved**: Explicit positive evidence found.
           - **Rejected**: Explicit exclusion found OR criteria not met.
           - **Insufficient Information**: Key details missing (e.g., policy type, waiting period status) and no default rule applies.
           
        3. **Payment Mode**: "cashless" ONLY if the hospital is explicitly listed as Network/PPN. Default to "reimbursement" if unsure or non-network.
        
        4. **Jusitification**: Must cite the exact section/clause used.
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
        - **Chain of Thought**: Before deciding, think through the coverage criteria step-by-step.
        - **Evidence-Based**: Every decision must be backed by a specific clause.
        - **Precision**: If the document doesn't explicitly cover the specific procedure/condition, state "insufficient_information" or "rejected" (if excluded), do not guess.
        - **Exclusions**: Check specifically for exclusions related to the query.
        
        Always respond with valid JSON in the specified format.
        """