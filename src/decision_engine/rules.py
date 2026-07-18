from typing import Optional, Dict, Any, Tuple
from src.core.models import ParsedQuery, DecisionResult

class RulesEngine:
    """Deterministic rules engine to pre-screen claims before LLM evaluation"""
    
    # Excluded procedures that are never covered
    STANDARD_EXCLUSIONS = {
        "cosmetic surgery", "cosmetic procedure", "aesthetic treatment", 
        "dental cleaning", "dental filling", "teeth whitening"
    }

    # Maximum claim amounts for automated processing
    AUTO_PAYMENT_CAP = 100000.0  # Claims above $100k need human review
    
    @classmethod
    def evaluate_rules(cls, parsed_query: ParsedQuery, context: Optional[Dict[str, Any]] = None) -> Optional[DecisionResult]:
        """
        Evaluate deterministic rules on parsed query.
        Returns a DecisionResult if a rule triggers (approved/rejected/pending),
        or None if no rules trigger (delegating to LLM).
        """
        context = context or {}
        
        # 1. Parse fields from query and context
        procedure = (
            parsed_query.structured_data.get("medical_procedure") or 
            context.get("procedure") or 
            ""
        ).lower().strip()
        
        claim_amount = parsed_query.structured_data.get("amount")
        if claim_amount is None:
            claim_amount = context.get("claim_amount")
        
        # Convert amount to float if possible
        if claim_amount is not None:
            try:
                claim_amount = float(claim_amount)
            except (ValueError, TypeError):
                claim_amount = None

        # 2. Rule: Explicit Exclusions
        for exclusion in cls.STANDARD_EXCLUSIONS:
            if exclusion in procedure:
                return DecisionResult(
                    decision="rejected",
                    payment_mode="unknown",
                    amount=0.0,
                    justification=f"Rule Rejection: The procedure '{procedure}' matches standard policy exclusion '{exclusion}'.",
                    source_clauses=["exclusion_standard_clause_01"],
                    confidence_score=1.0,
                    metadata={"rule_triggered": "standard_exclusion", "procedure": procedure}
                )

        # 3. Rule: Check extreme age thresholds (e.g., patients > 99 years)
        age = parsed_query.structured_data.get("age") or context.get("age")
        if age is not None:
            try:
                age_val = int(age)
                if age_val > 99 or age_val <= 0:
                    return DecisionResult(
                        decision="pending",
                        payment_mode="unknown",
                        amount=claim_amount,
                        justification=f"Rule flag: Patient age {age_val} is outside standard automated processing range (1-99). Forwarding for manual underwriting review.",
                        source_clauses=["underwriting_age_guideline"],
                        confidence_score=1.0,
                        metadata={"rule_triggered": "age_threshold_review", "age": age_val}
                    )
            except (ValueError, TypeError):
                pass

        # 4. Rule: Auto-escalate extremely large claims
        if claim_amount is not None and claim_amount > cls.AUTO_PAYMENT_CAP:
            return DecisionResult(
                decision="pending",
                payment_mode="unknown",
                amount=claim_amount,
                justification=f"Rule flag: Claim amount ${claim_amount:,.2f} exceeds standard automated approval cap of ${cls.AUTO_PAYMENT_CAP:,.2f}. Escalated to senior claims auditor.",
                source_clauses=["claims_escalation_threshold_v2"],
                confidence_score=1.0,
                metadata={"rule_triggered": "escalation_limit_exceeded", "amount": claim_amount}
            )
            
        return None
