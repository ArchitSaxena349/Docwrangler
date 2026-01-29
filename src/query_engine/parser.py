import re
from typing import Dict, Any, List
from google import genai
from core.models import ParsedQuery, QueryType
from core.config import Config

class QueryParser:
    """Parse natural language queries into structured data"""
    
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_name = Config.GEMINI_MODEL
    
    def parse_query(self, query: str) -> ParsedQuery:
        """Parse natural language query into structured format"""
        
        # Extract basic patterns
        structured_data = self._extract_patterns(query)
        
        # Use LLM for advanced parsing
        llm_parsed = self._llm_parse(query)
        structured_data.update(llm_parsed)
        
        # Determine query type
        query_type = self._determine_query_type(query, structured_data)
        
        # Extract key entities
        key_entities = self._extract_entities(query)
        
        # Determine intent
        intent = self._determine_intent(query, structured_data)
        
        return ParsedQuery(
            original_query=query,
            structured_data=structured_data,
            query_type=query_type,
            key_entities=key_entities,
            intent=intent
        )
    
    def _extract_patterns(self, query: str) -> Dict[str, Any]:
        """Extract common patterns using regex"""
        patterns = {}
        
        # Age pattern
        age_match = re.search(r'(\d+)[-\s]*(year|yr|y)[-\s]*old|(\d+)M|(\d+)F', query, re.IGNORECASE)
        if age_match:
            age = age_match.group(1) or age_match.group(3) or age_match.group(4)
            patterns['age'] = int(age)
            patterns['gender'] = 'male' if 'M' in age_match.group(0) else 'female' if 'F' in age_match.group(0) else None
        
        # Amount pattern
        amount_match = re.search(r'[\$₹]?(\d+(?:,\d+)*(?:\.\d+)?)', query)
        if amount_match:
            patterns['amount'] = float(amount_match.group(1).replace(',', ''))
        
        # Time period pattern
        time_match = re.search(r'(\d+)[-\s]*(month|year|day|week)', query, re.IGNORECASE)
        if time_match:
            patterns['time_period'] = {
                'value': int(time_match.group(1)),
                'unit': time_match.group(2).lower()
            }
        
        # Location pattern
        location_match = re.search(r'in\s+([A-Za-z\s]+?)(?:\s|,|$)', query, re.IGNORECASE)
        if location_match:
            patterns['location'] = location_match.group(1).strip()
        
        return patterns
    
    def _llm_parse(self, query: str) -> Dict[str, Any]:
        """Use LLM to extract structured information"""
        prompt = f"""
        Parse the following query and extract structured information:
        Query: "{query}"
        
        Extract and return JSON with these fields if present:
        - medical_procedure: any medical procedure mentioned
        - insurance_type: type of insurance
        - policy_details: policy-related information
        - claim_type: type of claim
        - urgency: urgency level
        - additional_context: any other relevant information
        
        Return only valid JSON:
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            import json
            # Extract JSON from response
            text = response.text
            # Try to find JSON in the response
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(text[json_start:json_end])
            return {}
        except:
            return {}
    
    def _determine_query_type(self, query: str, structured_data: Dict[str, Any]) -> QueryType:
        """Determine the type of query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['insurance', 'claim', 'policy', 'coverage']):
            return QueryType.INSURANCE_CLAIM
        elif any(word in query_lower for word in ['contract', 'agreement', 'terms']):
            return QueryType.CONTRACT_REVIEW
        elif any(word in query_lower for word in ['policy', 'rule', 'regulation']):
            return QueryType.POLICY_CHECK
        else:
            return QueryType.GENERAL
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract key entities from query"""
        entities = []
        
        # Medical procedures
        medical_terms = ['surgery', 'treatment', 'procedure', 'operation', 'therapy']
        for term in medical_terms:
            if term in query.lower():
                entities.append(term)
        
        # Insurance terms
        insurance_terms = ['policy', 'claim', 'coverage', 'premium', 'deductible']
        for term in insurance_terms:
            if term in query.lower():
                entities.append(term)
        
        return list(set(entities))
    
    def _determine_intent(self, query: str, structured_data: Dict[str, Any]) -> str:
        """Determine the intent of the query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['approve', 'covered', 'eligible']):
            return 'approval_check'
        elif any(word in query_lower for word in ['amount', 'payout', 'compensation']):
            return 'amount_calculation'
        elif any(word in query_lower for word in ['status', 'progress', 'update']):
            return 'status_inquiry'
        else:
            return 'general_inquiry'