from typing import Dict, Any, List

class MockGeminiModel:
    """Deterministic, context-aware Mock LLM for offline testing."""
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model_name = model_name

    def generate_content(self, prompt: str) -> Any:
        class Response:
            def __init__(self, text):
                self.text = text
        
        prompt_lower = prompt.lower()
        
        # 1. India / Grievance Redressal Rider Check
        if "india" in prompt_lower or "indian" in prompt_lower or "grievance" in prompt_lower or "consumer protection" in prompt_lower:
            ans = (
                "### NorthStar Retail - Indian Customer Jurisdiction Rider\n\n"
                "- **Applicable Policy:** **NSR-POL-RET-014, Section 10 & NSR-POL-SUP-005, Section 12**\n"
                "- **Statutory Protections:** Customers in India are protected under the Consumer Protection Act and E-Commerce Rules. Where statutory consumer rights are more favorable than standard store policy, Indian statutory terms apply.\n"
                "- **Grievance Redressal:** If standard support does not resolve your complaint, you may escalate directly to the designated **Grievance Officer** or approach the Consumer Disputes Redressal Commission."
            )
        # 2. Grocery Exclusions Check
        elif "grocery" in prompt_lower or "pasta" in prompt_lower or "chocolate" in prompt_lower or "tea" in prompt_lower or "almonds" in prompt_lower:
            ans = (
                "### NorthStar Retail Policy Evaluation\n\n"
                "- **Return Status:** **DECLINED (Non-Returnable)**\n"
                "- **Policy Reference:** **NSR-POL-RET-014, Section 4.1 (Grocery & Final Sale Exclusions)**\n"
                "- **Reasoning:** Grocery items are strictly non-returnable and excluded from refund eligibility regardless of condition, as they are perishable consumables that cannot be safely resold once delivered."
            )
        # 3. Denim Jacket Sizing Check
        elif "denim jacket" in prompt_lower or ("sizing" in prompt_lower and "jacket" in prompt_lower):
            ans = (
                "### NorthStar Retail Sizing & Exchange Advisory\n\n"
                "- **Sizing Recommendation:** Denim Jackets run approximately **one size small** compared to the standard sizing chart.\n"
                "- **Policy Reference:** **NSR-DOC-SIZ-001 (Apparel Sizing Guide)**\n"
                "- **Exchange Rule:** Customers are eligible for **1 free size exchange** per order within the 30-day return window. If between sizes, please size up."
            )
        # 4. Restocking fee / Condition Check
        elif "restocking fee" in prompt_lower or "packaging" in prompt_lower or "opened" in prompt_lower:
            ans = (
                "### NorthStar Retail Condition & Restocking Fee Assessment\n\n"
                "- **Policy Reference:** **NSR-POL-RET-014, Section 3.1**\n"
                "- **Condition Rule:** Items missing original packaging or tried beyond basic functional testing may be accepted subject to a **10% restocking fee** deduction from the refund amount."
            )
        # 5. Support SLA Check
        elif "sla" in prompt_lower or "support hours" in prompt_lower or "hours" in prompt_lower or "contact" in prompt_lower:
            ans = (
                "### NorthStar Retail Customer Support SLA\n\n"
                "- **Policy Reference:** **NSR-POL-SUP-005, Section 3.1 & Section 4**\n"
                "- **Support Hours:** Monday through Saturday, 9:00 AM – 7:00 PM local time.\n"
                "- **Standard Ticket SLA:** Resolved within 24 hours.\n"
                "- **Complex / Warranty Inspection SLA:** Up to 7 Business Days."
            )
        else:
            ans = (
                "### NorthStar Retail Policy Summary\n\n"
                "According to NorthStar Retail Store Policies (NSR-POL-RET-014 / NSR-POL-SUP-005):\n"
                "- Standard return window is 30 days from carrier delivery date.\n"
                "- Refunds are issued within 5-7 business days to the original payment method.\n"
                "- Items in non-standard condition may incur a 10% restocking fee."
            )
            
        return Response(ans)
