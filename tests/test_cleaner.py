import pytest
import pandas as pd
from src.pipeline.cleaner import clean_retail_data, parse_date_safely

def test_parse_date_safely():
    assert parse_date_safely("2026/08/26") == "2026-08-26"
    assert parse_date_safely("2026-07-01") == "2026-07-01"
    assert parse_date_safely("") == "2026-01-01"

def test_clean_retail_data():
    raw_data = pd.DataFrame([
        {"order_id": "ORD-1", "order_date": "2026/05/10", "store_id": "ST-1", "product_id": "SKU-BE-001", "product_name": "", "category": "Beauty", "quantity": "2", "unit_price": "", "region": "East"},
        {"order_id": "ORD-2", "order_date": "2026-06-01", "store_id": "ST-2", "product_id": "SKU-GR-004", "product_name": "Whole Wheat Pasta 1kg", "category": "Grocery", "quantity": "-3", "unit_price": "1.99", "region": "West"},
        {"order_id": "ORD-3", "order_date": "2026-07-01", "store_id": "ST-3", "product_id": "SKU-AP-003", "product_name": "Denim Jacket", "category": "Apparel", "quantity": "", "unit_price": "23.99", "region": "Central"}
    ])
    
    cleaned, metrics = clean_retail_data(raw_data)
    
    assert len(cleaned) == 3
    # Test imputation
    assert cleaned.loc[0, "product_name"] == "Aloe Vera Gel 200ml"
    assert cleaned.loc[0, "unit_price"] == 2.49
    assert cleaned.loc[0, "order_date"] == "2026-05-10"
    
    # Test return flag
    assert cleaned.loc[1, "is_return"] == True
    assert cleaned.loc[1, "refund_amount"] == 5.97
    assert cleaned.loc[1, "is_grocery"] == True
    assert cleaned.loc[1, "policy_returnable"] == False

    # Test missing quantity imputation
    assert cleaned.loc[2, "quantity"] == 1
    assert metrics["sales_transactions"] == 2
    assert metrics["return_transactions"] == 1
