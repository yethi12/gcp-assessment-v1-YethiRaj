-- =============================================================================
-- NorthStar Retail - BigQuery / Dataform Gold Layer Dimensional Schema
-- =============================================================================

-- 1. Product Dimension
CREATE OR REPLACE TABLE `northstar-retail-dev.northstar_retail_mart.dim_products` (
    product_id STRING OPTIONS(description="Unique SKU identifier"),
    product_name STRING OPTIONS(description="Standardized product name"),
    category STRING OPTIONS(description="Product category"),
    unit_price FLOAT64 OPTIONS(description="Default retail catalog unit price"),
    is_returnable BOOL OPTIONS(description="False for Grocery & Final Sale, True otherwise")
)
CLUSTER BY category, product_id;

-- 2. Store Dimension
CREATE OR REPLACE TABLE `northstar-retail-dev.northstar_retail_mart.dim_stores` (
    store_id STRING OPTIONS(description="Store identifier"),
    region STRING OPTIONS(description="Geographic operational region")
)
CLUSTER BY region;

-- 3. Date Dimension
CREATE OR REPLACE TABLE `northstar-retail-dev.northstar_retail_mart.dim_dates` (
    date_key INT64 OPTIONS(description="Integer key YYYYMMDD"),
    order_date DATE OPTIONS(description="Standardized date"),
    year INT64,
    month INT64,
    day INT64,
    day_name STRING,
    quarter INT64
)
CLUSTER BY year, month;

-- 4. Fact Orders (Gross Sales)
CREATE OR REPLACE TABLE `northstar-retail-dev.northstar_retail_mart.fact_orders` (
    order_id STRING,
    date_key INT64,
    order_date DATE,
    store_id STRING,
    product_id STRING,
    quantity INT64,
    unit_price FLOAT64,
    total_amount FLOAT64
)
PARTITION BY order_date
CLUSTER BY store_id, product_id;

-- 5. Fact Returns
CREATE OR REPLACE TABLE `northstar-retail-dev.northstar_retail_mart.fact_returns` (
    order_id STRING,
    date_key INT64,
    order_date DATE,
    store_id STRING,
    product_id STRING,
    quantity_returned INT64,
    unit_price FLOAT64,
    refund_amount FLOAT64
)
PARTITION BY order_date
CLUSTER BY store_id, product_id;
