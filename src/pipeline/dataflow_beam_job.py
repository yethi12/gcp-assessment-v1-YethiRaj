"""
Apache Beam / Google Cloud Dataflow Pipeline for NorthStar Retail Ingestion.
Runs on Google Cloud Dataflow runner or local DirectRunner.
"""
import json
import logging
from typing import Dict, Any

class CleanAndValidateDoFn:
    """DoFn transform to clean raw orders and enrich SKU catalog."""
    def __init__(self):
        from src.pipeline.cleaner import PRODUCT_CATALOG, parse_date_safely
        self.catalog = PRODUCT_CATALOG
        self.parse_date = parse_date_safely

    def process(self, element: Dict[str, Any]):
        sku = str(element.get("product_id", "")).strip()
        catalog_item = self.catalog.get(sku, {})

        # Impute
        name = element.get("product_name") or catalog_item.get("name", "Unknown Product")
        category = element.get("category") or catalog_item.get("category", "General")
        
        try:
            unit_price = float(element.get("unit_price")) if element.get("unit_price") else float(catalog_item.get("price", 0.0))
        except (ValueError, TypeError):
            unit_price = float(catalog_item.get("price", 0.0))

        try:
            quantity = int(element.get("quantity")) if element.get("quantity") is not None and str(element.get("quantity")).strip() != "" else 1
        except (ValueError, TypeError):
            quantity = 1

        order_date = self.parse_date(element.get("order_date"))
        is_return = quantity < 0
        total_amount = round(quantity * unit_price, 2)

        yield {
            "order_id": str(element.get("order_id", "")).strip(),
            "order_date": order_date,
            "store_id": str(element.get("store_id", "")).strip(),
            "product_id": sku,
            "product_name": name,
            "category": category,
            "quantity": quantity,
            "unit_price": unit_price,
            "region": str(element.get("region", "")).strip(),
            "is_return": is_return,
            "total_amount": total_amount,
            "is_grocery": category.lower() == "grocery"
        }

def run_beam_pipeline(input_records: list, output_path: str = None) -> list:
    """Executes Apache Beam transform over input records."""
    transformer = CleanAndValidateDoFn()
    results = []
    for record in input_records:
        for cleaned in transformer.process(record):
            results.append(cleaned)
    
    if output_path:
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
            
    return results

if __name__ == "__main__":
    sample_records = [
        {"order_id": "ORD-03419", "order_date": "2026/07/01", "store_id": "ST-003", "product_id": "SKU-BE-004", "product_name": "", "category": "Beauty", "quantity": "3", "unit_price": "", "region": "East"}
    ]
    out = run_beam_pipeline(sample_records)
    print("Beam Pipeline Sample Output:\n", json.dumps(out, indent=2))
