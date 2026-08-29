import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.pipeline.data_transformer import DataTransformer
from src.config import settings

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_pipeline_data():
    raw_file = settings.DATA_DIR / "raw" / "orders.csv"
    transformer = DataTransformer(settings.PROCESSED_DIR)
    transformer.run_pipeline(str(raw_file))

def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_api_agent_query():
    res = client.post("/agent/query", json={"query": "What is the return window for NorthStar Retail?"})
    assert res.status_code == 200
    data = res.json()
    assert "response" in data

def test_api_return_evaluation():
    res = client.post("/returns/evaluate", json={
        "order_id": "ORD-03419",
        "days_since_delivery": 15,
        "item_condition": "like_new_with_packaging",
        "country": "US"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["eligible"] is True
    assert data["product_name"] == "Hand Cream 100ml"

def test_api_analytics_summary():
    res = client.get("/analytics/summary")
    assert res.status_code == 200
    data = res.json()
    assert "sales" in data
    assert "returns" in data
    assert "net_revenue" in data
