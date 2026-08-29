# Assumptions and Limitations

## 1. Architectural Assumptions
- **Hyperscaler Selection**: Google Cloud Platform (GCP) was selected as the target cloud provider for modern serverless BigQuery dimensional modeling, Dataflow (Apache Beam) stream/batch processing, Cloud Composer (Airflow), and Vertex AI Gemini models.
- **Dual-Mode Execution**: The architecture guarantees zero-dependency offline reproducibility. When `EXECUTION_MODE=mock`, all components seamlessly use DuckDB / SQLite, local in-memory Pub/Sub, and local vector embeddings without requiring active GCP project credentials or network connectivity.
- **Medallion Schema Architecture**:
  - **Bronze (Raw)**: Preserves original, immutable incoming transactions.
  - **Silver (Cleaned)**: Normalizes date representations, imputes missing names and prices from the master SKU catalog, and segregates return events.
  - **Gold (Analytical)**: Conformed Star Schema (`dim_products`, `dim_stores`, `dim_dates`, `fact_orders`, `fact_returns`) optimized for high-throughput OLAP querying.

## 2. Business Logic & Imputation Rules
- **Missing SKU Attributes**: If `product_name`, `category`, or `unit_price` is missing from an order row, the pipeline automatically looks up the `product_id` (e.g. `SKU-BE-004`) in the authoritative `PRODUCT_CATALOG` to perform lossless deterministic imputation.
- **Missing Quantity**: If `quantity` is null or empty, it is imputed with a default value of `1`.
- **Negative Quantities (Returns)**: Negative quantities represent return/refund transactions. They are segregated into `fact_returns` with positive refund amounts for accounting reconciliation, while positive sales are routed to `fact_orders`.
- **Grocery Category Non-Returnability**: Strictly enforced under **NSR-POL-RET-014, Section 4.1**. Grocery items are marked `is_returnable = False` and cannot be authorized for returns.
- **Apparel Sizing Exception**: Denim Jackets (`SKU-AP-003`) are explicitly flagged as running 1 size small pursuant to **NSR-DOC-SIZ-001**, advising customers to size up.
- **Restocking Fee Rule**: Items with opened or missing packaging are assessed a **10% restocking fee** deduction from the gross refund per **NSR-POL-RET-014, Section 3.1**.
- **India Jurisdiction Rider**: Pursuant to **NSR-POL-RET-014, Section 10** and **NSR-POL-SUP-005, Section 12**, Indian consumers have statutory rights under the Consumer Protection Act and can escalate to the designated Grievance Officer.

## 3. Known Limitations
- **Live Vertex AI Quota / API Keys**: Live Gemini LLM generation requires an active `GEMINI_API_KEY` or GCP Application Default Credentials (ADC). When omitted, the built-in deterministic `MockGeminiModel` executes locally with full policy accuracy.
- **Historical SCD Tracking**: The current dimensional model implements SCD Type 1 (overwrite). In future enterprise iterations, SCD Type 2 can be enabled via Dataform snapshots to track price changes over time.
