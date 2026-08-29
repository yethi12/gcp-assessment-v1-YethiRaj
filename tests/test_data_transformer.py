import pytest
import pandas as pd
from pathlib import Path
from src.pipeline.data_transformer import DataTransformer

def test_data_transformer_pipeline(tmp_path):
    raw_csv = tmp_path / "test_orders.csv"
    raw_data = pd.DataFrame([
        {"order_id": "ORD-001", "order_date": "2026-07-01", "store_id": "ST-003", "product_id": "SKU-BE-004", "product_name": "Hand Cream 100ml", "category": "Beauty", "quantity": 3, "unit_price": 1.99, "region": "East"},
        {"order_id": "ORD-002", "order_date": "2026-07-02", "store_id": "ST-003", "product_id": "SKU-GR-004", "product_name": "Whole Wheat Pasta 1kg", "category": "Grocery", "quantity": -2, "unit_price": 1.99, "region": "East"}
    ])
    raw_data.to_csv(raw_csv, index=False)
    
    transformer = DataTransformer(output_dir=tmp_path / "processed")
    result = transformer.run_pipeline(str(raw_csv))
    
    assert "metrics" in result
    assert "dim_products" in result["tables_created"]
    assert "fact_orders" in result["tables_created"]
    assert "fact_returns" in result["tables_created"]
    
    # Check generated files
    assert (tmp_path / "processed" / "dim_products.parquet").exists()
    assert (tmp_path / "processed" / "fact_orders.parquet").exists()
    assert (tmp_path / "processed" / "fact_returns.parquet").exists()
