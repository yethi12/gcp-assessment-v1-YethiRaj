# NorthStar Retail - GCP Analytics & AI Policy Engine

An enterprise-grade Google Cloud Platform (GCP) Data Engineering pipeline and Generative AI Policy Reasoning Engine designed for NorthStar Retail.

---

## 🌟 Key Features

1. **Robust Data Ingestion & Cleansing (Dataflow / Apache Beam / Python)**
   - Schema enforcement, date standardization (`YYYY-MM-DD` and `YYYY/MM/DD`), and anomaly detection.
   - Master SKU catalog lookup for deterministic imputation of missing product names, categories, and unit prices.
   - Clean segregation of gross sales transactions and return/refund events.
2. **BigQuery Medallion Dimensional Modeling**
   - **Bronze**: Raw immutable ingestion layer.
   - **Silver**: Cleaned and enriched staging layer.
   - **Gold**: Conformed Star Schema (`dim_products`, `dim_stores`, `dim_dates`, `fact_orders`, `fact_returns`, `agg_category_performance`, `agg_store_performance`).
3. **Generative AI Policy Assistant & RAG Engine (Gemini / Vertex AI)**
   - Multi-document RAG over NorthStar Retail policies:
     - Return & Refund Policy (`NSR-POL-RET-014`)
     - Customer Support Policy (`NSR-POL-SUP-005`)
     - Apparel Sizing Guide (`NSR-DOC-SIZ-001`)
     - Stationery Category Guidelines
   - Dynamic Function & Tool Calling (`lookup_order`, `evaluate_return_eligibility`, `calculate_refund_amount`, `get_sizing_guideline`).
   - Handles edge cases: Grocery exclusions, 10% restocking fees on opened packaging, 1 size small Denim Jacket adjustments, and Indian Consumer Protection Act Grievance Officer escalation riders.
4. **Dual-Mode Execution (100% Zero-Credential Local Mock + Live GCP)**
   - Test and evaluate the entire pipeline and AI agent on any machine without requiring active cloud credentials or paid API keys.
5. **Infrastructure as Code (Terraform) & CI/CD**
   - Modular Terraform configurations (`gcs.tf`, `bigquery.tf`, `pubsub.tf`, `iam.tf`).
   - GitHub Actions workflow testing code quality, unit tests, and end-to-end integration.

---

## 📐 System Architecture

```
[Raw Orders & Policy Docs] ──> [GCS Landing Bucket]
                                     │
                                     ▼
                     [Apache Beam / Dataflow Cleaner]
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
        [BigQuery Staging]                       [Policy Chunker & RAG]
                 │                                       │
                 ▼                                       ▼
    [Gold Star Schema Models]                 [Vector Embeddings Store]
   (dim_products, fact_orders,                           │
    fact_returns, agg_metrics)                           ▼
                 │                          [Gemini AI Policy Agent]
                 └────────── Tool Calling ───────────────┘
                                     │
                                     ▼
                   [FastAPI REST API & Interactive CLI]
```

---

## 🚀 Quickstart & Execution

### 1. Clone & Setup Environment
```bash
git clone <repository_url>
cd gcp-assessment-v1-candidate

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Data Engineering Pipeline
Process raw transactions and generate the analytical dimensional mart:
```bash
python -m src.pipeline.data_transformer
```
*Outputs generated in `data/processed/` (`.parquet`, `.csv`, and SQLite/DuckDB database).*

### 3. Run AI Policy Agent (CLI)
Ask any customer policy or order inquiry:
```bash
# Grocery exclusion test:
python -m src.agent.policy_agent --query "Can I return order ORD-01383 which contains pasta?"

# Sizing recommendation test:
python -m src.agent.policy_agent --query "I bought a Denim Jacket, what size should I get?"

# Indian customer rights test:
python -m src.agent.policy_agent --query "I am a customer in India with an unresolved issue, what can I do?" --country IN
```

### 4. Launch REST API Server
```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger UI available at: `http://127.0.0.1:8000/docs`

---

## 🧪 Testing

Run the full automated test suite with pytest:
```bash
pytest tests/ -v
```

---

## 🛡️ Security & Privacy
- **Zero Real PII**: Uses only mock transaction data generated for the assessment.
- **No Committed Secrets**: `.env` is excluded in `.gitignore`; `.env.example` provides template configurations.
- **Least-Privilege IAM**: Terraform provisions service accounts with minimal required roles (`roles/bigquery.dataEditor`, `roles/storage.objectAdmin`, `roles/aiplatform.user`).

---

## 🤖 AI Tool Usage Disclosure
Development utilized AI-assisted pair programming tools for boilerplate generation, test scaffolding, and documentation alignment in accordance with hackathon guidelines.
