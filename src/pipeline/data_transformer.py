import os
import pandas as pd
import duckdb
from pathlib import Path
from typing import Dict, Any
from src.pipeline.cleaner import clean_retail_data

class DataTransformer:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.output_dir / "northstar_analytics.duckdb"

    def build_dimensional_models(self, df_cleaned: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Builds Gold layer star schema tables from cleaned silver dataset."""
        
        # 1. Dimension: Products
        dim_products = df_cleaned[["product_id", "product_name", "category", "unit_price", "policy_returnable"]].drop_duplicates(subset=["product_id"]).reset_index(drop=True)
        dim_products.rename(columns={"policy_returnable": "is_returnable"}, inplace=True)

        # 2. Dimension: Stores
        dim_stores = df_cleaned[["store_id", "region"]].drop_duplicates(subset=["store_id"]).reset_index(drop=True)

        # 3. Dimension: Dates
        dates = pd.to_datetime(df_cleaned["order_date"].unique())
        dim_dates = pd.DataFrame({
            "order_date": dates.strftime("%Y-%m-%d"),
            "date_key": dates.strftime("%Y%m%d").astype(int),
            "year": dates.year,
            "month": dates.month,
            "day": dates.day,
            "day_name": dates.day_name(),
            "quarter": dates.quarter
        }).sort_values("order_date").reset_index(drop=True)

        # 4. Fact: Orders (Gross Sales transactions)
        sales_df = df_cleaned[~df_cleaned["is_return"]].copy()
        sales_df["date_key"] = pd.to_datetime(sales_df["order_date"]).dt.strftime("%Y%m%d").astype(int)
        fact_orders = sales_df[[
            "order_id", "date_key", "store_id", "product_id", "quantity", "unit_price", "total_amount"
        ]].reset_index(drop=True)

        # 5. Fact: Returns
        returns_df = df_cleaned[df_cleaned["is_return"]].copy()
        returns_df["date_key"] = pd.to_datetime(returns_df["order_date"]).dt.strftime("%Y%m%d").astype(int)
        fact_returns = returns_df[[
            "order_id", "date_key", "store_id", "product_id", "absolute_quantity", "unit_price", "refund_amount"
        ]].rename(columns={"absolute_quantity": "quantity_returned"}).reset_index(drop=True)

        # 6. Aggregated Mart: Category Performance
        agg_category = df_cleaned.groupby("category").agg(
            total_orders=("order_id", "count"),
            gross_sales=("net_sales_amount", "sum"),
            refunds=("refund_amount", "sum"),
            net_revenue=("total_amount", "sum"),
            units_sold=("quantity", lambda q: q[q > 0].sum()),
            units_returned=("quantity", lambda q: q[q < 0].abs().sum())
        ).reset_index()

        # 7. Aggregated Mart: Regional Store Performance
        agg_store = df_cleaned.groupby(["region", "store_id"]).agg(
            total_transactions=("order_id", "count"),
            net_revenue=("total_amount", "sum"),
            refund_value=("refund_amount", "sum")
        ).reset_index()

        models = {
            "stg_orders_cleaned": df_cleaned,
            "dim_products": dim_products,
            "dim_stores": dim_stores,
            "dim_dates": dim_dates,
            "fact_orders": fact_orders,
            "fact_returns": fact_returns,
            "agg_category_performance": agg_category,
            "agg_store_performance": agg_store
        }

        # Persist to local DuckDB and Parquet/CSV
        con = duckdb.connect(str(self.db_path))
        for table_name, df_table in models.items():
            df_table.to_parquet(self.output_dir / f"{table_name}.parquet", index=False)
            df_table.to_csv(self.output_dir / f"{table_name}.csv", index=False)
            con.register("temp_df", df_table)
            con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_df")
        con.close()

        return models

    def run_pipeline(self, raw_csv_path: str) -> Dict[str, Any]:
        """Runs end-to-end transformation pipeline."""
        df_raw = pd.read_csv(raw_csv_path)
        df_cleaned, metrics = clean_retail_data(df_raw)
        models = self.build_dimensional_models(df_cleaned)
        
        return {
            "metrics": metrics,
            "tables_created": list(models.keys()),
            "db_path": str(self.db_path)
        }
