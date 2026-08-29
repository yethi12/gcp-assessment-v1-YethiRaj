import pytest
from pathlib import Path
from src.agent.rag_engine import PolicyRAGEngine
from src.config import settings

def test_policy_rag_engine():
    policy_path = settings.DATA_DIR / "raw" / "policies.json"
    engine = PolicyRAGEngine(policy_path)
    
    assert len(engine.chunks) > 0
    
    # Test grocery exclusion retrieval
    results = engine.retrieve("Can I return grocery items like pasta or almonds?", top_k=2)
    assert len(results) > 0
    top_doc = results[0]
    assert "NSR-POL-RET-014" in top_doc["doc_id"]
    assert "Grocery" in top_doc["section_title"] or "Exclusions" in top_doc["section_title"]

    # Test sizing guide retrieval
    results_sizing = engine.retrieve("Denim jacket sizing guidance", top_k=2)
    assert len(results_sizing) > 0
    assert any("SIZ" in r["doc_id"] for r in results_sizing)
