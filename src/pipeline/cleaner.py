import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, Dict, Any

# Master product catalog for imputation and validation
PRODUCT_CATALOG: Dict[str, Dict[str, Any]] = {
    "SKU-BE-001": {"name": "Aloe Vera Gel 200ml", "category": "Beauty", "price": 2.49, "returnable": True},
    "SKU-BE-002": {"name": "Sunscreen SPF 50", "category": "Beauty", "price": 5.49, "returnable": True},
    "SKU-BE-003": {"name": "Shampoo 400ml", "category": "Beauty", "price": 3.49, "returnable": True},
    "SKU-BE-004": {"name": "Hand Cream 100ml", "category": "Beauty", "price": 1.99, "returnable": True},
    "SKU-BE-005": {"name": "Lip Balm Pack of 3", "category": "Beauty", "price": 1.49, "returnable": True},
    "SKU-TY-001": {"name": "Wooden Puzzle Set", "category": "Toys", "price": 7.99, "returnable": True},
    "SKU-TY-002": {"name": "Building Blocks 100pc", "category": "Toys", "price": 12.99, "returnable": True},
    "SKU-TY-003": {"name": "Plush Bear Medium", "category": "Toys", "price": 6.49, "returnable": True},
    "SKU-TY-004": {"name": "Board Game Family Pack", "category": "Toys", "price": 14.99, "returnable": True},
    "SKU-TY-005": {"name": "Remote Control Car", "category": "Toys", "price": 16.99, "returnable": True},
    "SKU-HM-001": {"name": "Ceramic Mug Set", "category": "Home", "price": 5.99, "returnable": True},
    "SKU-HM-002": {"name": "LED Desk Lamp", "category": "Home", "price": 11.99, "returnable": True},
    "SKU-HM-003": {"name": "Cotton Bedsheet Set", "category": "Home", "price": 14.99, "returnable": True},
    "SKU-HM-004": {"name": "Non-stick Pan 24cm", "category": "Home", "price": 9.99, "returnable": True},
    "SKU-HM-005": {"name": "Storage Basket Set", "category": "Home", "price": 6.99, "returnable": True},
    "SKU-AP-001": {"name": "Cotton T-Shirt", "category": "Apparel", "price": 4.99, "returnable": True},
    "SKU-AP-002": {"name": "Running Shoes", "category": "Apparel", "price": 29.99, "returnable": True},
    "SKU-AP-003": {"name": "Denim Jacket", "category": "Apparel", "price": 23.99, "returnable": True},
    "SKU-AP-004": {"name": "Wool Socks 3-pack", "category": "Apparel", "price": 3.49, "returnable": True},
    "SKU-AP-005": {"name": "Rain Jacket", "category": "Apparel", "price": 18.99, "returnable": True},
    "SKU-GR-001": {"name": "Organic Almonds 500g", "category": "Grocery", "price": 6.49, "returnable": False},
    "SKU-GR-002": {"name": "Green Tea Box 25pk", "category": "Grocery", "price": 2.49, "returnable": False},
    "SKU-GR-003": {"name": "Extra Virgin Olive Oil 1L", "category": "Grocery", "price": 8.99, "returnable": False},
    "SKU-GR-004": {"name": "Whole Wheat Pasta 1kg", "category": "Grocery", "price": 1.99, "returnable": False},
    "SKU-GR-005": {"name": "Dark Chocolate Bar", "category": "Grocery", "price": 1.79, "returnable": False},
    "SKU-EL-001": {"name": "Wireless Earbuds", "category": "Electronics", "price": 18.49, "returnable": True},
    "SKU-EL-002": {"name": "USB-C Charger 30W", "category": "Electronics", "price": 8.99, "returnable": True},
    "SKU-EL-003": {"name": "Bluetooth Speaker", "category": "Electronics", "price": 24.99, "returnable": True},
    "SKU-EL-004": {"name": "Power Bank 10000mAh", "category": "Electronics", "price": 12.99, "returnable": True},
    "SKU-EL-005": {"name": "Smartwatch Band", "category": "Electronics", "price": 7.99, "returnable": True},
    "SKU-ST-001": {"name": "Notebook A5 Ruled", "category": "Stationery", "price": 1.29, "returnable": True},
    "SKU-ST-002": {"name": "Gel Pen Pack of 10", "category": "Stationery", "price": 1.49, "returnable": True},
    "SKU-ST-003": {"name": "Desk Organizer", "category": "Stationery", "price": 5.99, "returnable": True},
    "SKU-ST-004": {"name": "Sticky Notes Set", "category": "Stationery", "price": 0.99, "returnable": True},
}

def parse_date_safely(date_str: Any) -> str:
    """Parses multiple date formats (YYYY-MM-DD, YYYY/MM/DD) to ISO format."""
    if pd.isna(date_str) or not str(date_str).strip():
        return "2026-01-01"
    s = str(date_str).strip().replace("/", "-")
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return s

def clean_retail_data(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans raw retail transaction data:
    - Standardizes date formats
    - Imputes missing product_name, category, unit_price from master catalog
    - Flags returns vs gross sales
    - Imputes missing quantities
    - Computes data quality metrics
    """
    df = df_raw.copy()
    initial_rows = len(df)
    
    # 1. Clean column names
    df.columns = [c.strip().lower() for c in df.columns]
    
    # 2. Date normalization
    df["order_date"] = df["order_date"].apply(parse_date_safely)
    
    # Standardize empty strings and numeric types upfront
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    
    missing_name_count = 0
    missing_price_count = 0
    missing_qty_count = int(df["quantity"].isna().sum())
    
    # 3. Product Catalog Enrichment & Missing Value Imputation
    for idx in df.index:
        sku = str(df.loc[idx, "product_id"]).strip()
        catalog_entry = PRODUCT_CATALOG.get(sku)
        
        if catalog_entry:
            # Impute product_name if missing
            cur_name = df.loc[idx, "product_name"]
            if pd.isna(cur_name) or not str(cur_name).strip():
                df.loc[idx, "product_name"] = catalog_entry["name"]
                missing_name_count += 1
            
            # Impute category if missing
            cur_cat = df.loc[idx, "category"]
            if pd.isna(cur_cat) or not str(cur_cat).strip():
                df.loc[idx, "category"] = catalog_entry["category"]
                
            # Impute unit_price if missing
            cur_price = df.loc[idx, "unit_price"]
            if pd.isna(cur_price):
                df.loc[idx, "unit_price"] = float(catalog_entry["price"])
                missing_price_count += 1

    # 4. Fill missing quantities with default 1
    df["quantity"] = df["quantity"].fillna(1).astype(int)
    df["unit_price"] = df["unit_price"].fillna(0.0).astype(float)
    
    # 5. Classify Transactions (Sales vs Returns)
    df["is_return"] = df["quantity"] < 0
    df["transaction_type"] = np.where(df["is_return"], "RETURN", "SALE")
    df["absolute_quantity"] = df["quantity"].abs()
    df["total_amount"] = (df["quantity"] * df["unit_price"]).round(2)
    df["net_sales_amount"] = np.where(df["is_return"], 0.0, df["total_amount"])
    df["refund_amount"] = np.where(df["is_return"], (df["absolute_quantity"] * df["unit_price"]).round(2), 0.0)

    # 6. Policy Flags
    df["is_grocery"] = df["category"].astype(str).str.lower() == "grocery"
    df["policy_returnable"] = ~df["is_grocery"]
    
    metrics = {
        "total_records_processed": initial_rows,
        "sales_transactions": int((~df["is_return"]).sum()),
        "return_transactions": int(df["is_return"].sum()),
        "imputed_missing_names": missing_name_count,
        "imputed_missing_prices": missing_price_count,
        "imputed_missing_quantities": missing_qty_count,
        "total_gross_revenue": round(float(df[~df["is_return"]]["total_amount"].sum()), 2),
        "total_refund_value": round(float(df[df["is_return"]]["total_amount"].abs().sum()), 2),
        "total_net_revenue": round(float(df["total_amount"].sum()), 2)
    }
    
    return df, metrics
