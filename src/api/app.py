from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.agent.policy_agent import NorthStarPolicyAgent
from src.agent.tools import RetailTools
from src.config import settings
import duckdb
import pandas as pd

app = FastAPI(
    title="NorthStar Retail Analytics & Policy AI API",
    version="1.0.0",
    description="Enterprise API providing Retail Analytics, Policy Intelligence, and Customer Support RAG Agent."
)

agent = NorthStarPolicyAgent()
tools = RetailTools()

class QueryRequest(BaseModel):
    query: str
    country: Optional[str] = "US"

class ReturnEvaluationRequest(BaseModel):
    order_id: str
    days_since_delivery: int = 10
    item_condition: str = "like_new_with_packaging"
    country: str = "US"

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "mode": settings.EXECUTION_MODE,
        "service": "NorthStar Retail API"
    }

@app.post("/agent/query")
def ask_agent(req: QueryRequest):
    result = agent.answer_query(req.query, country=req.country)
    return result

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    res = tools.lookup_order(order_id)
    if not res.get("found"):
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")
    return res

@app.post("/returns/evaluate")
def evaluate_return(req: ReturnEvaluationRequest):
    return tools.evaluate_return_eligibility(
        order_id=req.order_id,
        days_since_delivery=req.days_since_delivery,
        item_condition=req.item_condition,
        country=req.country
    )

@app.get("/analytics/summary")
def get_analytics_summary():
    db_path = settings.PROCESSED_DIR / "northstar_analytics.duckdb"
    if not db_path.exists():
        return {"status": "pending_transformation", "message": "Run pipeline to generate mart."}
    
    con = duckdb.connect(str(db_path))
    try:
        sales_summary = con.execute("""
            SELECT 
                COUNT(*) as total_sales_orders,
                ROUND(SUM(total_amount), 2) as gross_revenue
            FROM fact_orders
        """).df().to_dict(orient="records")[0]

        returns_summary = con.execute("""
            SELECT 
                COUNT(*) as total_returns,
                ROUND(SUM(refund_amount), 2) as total_refunded
            FROM fact_returns
        """).df().to_dict(orient="records")[0]

        return {
            "sales": sales_summary,
            "returns": returns_summary,
            "net_revenue": round(sales_summary["gross_revenue"] - returns_summary["total_refunded"], 2)
        }
    finally:
        con.close()
