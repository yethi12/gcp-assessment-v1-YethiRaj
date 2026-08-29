import re
import argparse
from typing import Dict, Any, Optional
from src.config import settings
from src.agent.rag_engine import PolicyRAGEngine
from src.agent.tools import RetailTools
from src.agent.prompts import AGENT_SYSTEM_PROMPT, format_rag_prompt
from src.mocks.mock_llm import MockGeminiModel

class NorthStarPolicyAgent:
    """End-to-End AI Assistant for Policy Reasoning and Order Assessment."""
    def __init__(self):
        self.rag_engine = PolicyRAGEngine(settings.DATA_DIR / "raw" / "policies.json")
        self.tools = RetailTools()
        self.llm = self._init_llm()

    def _init_llm(self):
        if settings.EXECUTION_MODE == "gcp" or (settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 5):
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                return genai.GenerativeModel(settings.GEMINI_MODEL, system_instruction=AGENT_SYSTEM_PROMPT)
            except Exception as e:
                print(f"[Warning] Failed to initialize live Gemini model ({e}). Using mock LLM.")
                return MockGeminiModel()
        return MockGeminiModel()

    def answer_query(self, query: str, country: str = "US") -> Dict[str, Any]:
        # 1. Check if an Order ID is mentioned in the query
        order_match = re.search(r"\b(ORD-\d{5})\b", query, re.IGNORECASE)
        tool_results = {}
        if order_match:
            order_id = order_match.group(1).upper()
            order_lookup = self.tools.lookup_order(order_id)
            if order_lookup.get("found"):
                # Run deterministic return evaluation tool
                eval_res = self.tools.evaluate_return_eligibility(
                    order_id=order_id,
                    days_since_delivery=10,
                    item_condition="standard",
                    country=country
                )
                tool_results = {
                    "order_details": order_lookup["order"],
                    "return_evaluation": eval_res
                }

        # 2. Retrieve relevant policy chunks
        retrieved_docs = self.rag_engine.retrieve(query, top_k=3)

        # 3. Format Prompt & Generate Response
        prompt = format_rag_prompt(query, retrieved_docs, tool_results)
        response = self.llm.generate_content(prompt)

        return {
            "query": query,
            "response": response.text,
            "citations": [f"{doc['doc_id']} Sec {doc['section_id']}" for doc in retrieved_docs],
            "tool_output": tool_results
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NorthStar Retail Policy Assistant")
    parser.add_argument("--query", type=str, default="Can I return order ORD-01383 which contains pasta?", help="Customer query")
    parser.add_argument("--country", type=str, default="US", help="Customer country")
    args = parser.parse_args()

    agent = NorthStarPolicyAgent()
    res = agent.answer_query(args.query, country=args.country)
    print("\n================ AGENT RESPONSE ================")
    print(res["response"])
    print("================================================\n")
    print("Citations:", res["citations"])
