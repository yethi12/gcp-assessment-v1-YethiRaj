import pytest
from src.agent.tools import RetailTools
from src.agent.policy_agent import NorthStarPolicyAgent

def test_retail_tools():
    tools = RetailTools()
    
    # Test sizing tool
    sizing = tools.get_sizing_guideline("Denim Jacket")
    assert "1 size small" in sizing["sizing_note"]
    assert sizing["free_exchange_allowed"] is True

def test_policy_agent_grocery_query():
    agent = NorthStarPolicyAgent()
    res = agent.answer_query("Can I return order ORD-01383 which contains pasta?")
    
    assert "response" in res
    assert "NSR-POL-RET-014" in str(res["response"]) or any("NSR-POL-RET-014" in c for c in res["citations"])

def test_policy_agent_india_rider():
    agent = NorthStarPolicyAgent()
    res = agent.answer_query("I am an Indian consumer with an unresolved complaint", country="IN")
    
    assert "response" in res
    assert "India" in res["response"] or "Grievance" in res["response"] or "Consumer Protection" in res["response"]
