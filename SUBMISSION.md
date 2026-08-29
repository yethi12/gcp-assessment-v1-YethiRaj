# HCLTech Assessment Submission Form

**Candidate Name:** [Your Full Name]  
**Candidate Email ID:** [Your Email Address]  
**Assigned Slot:** [Your Assigned Slot / Date]  
**Repository URL:** https://github.com/[Your-Username]/gcp-assessment-v1-[your-name]  
**Final Pull Request URL:** https://github.com/[Your-Username]/gcp-assessment-v1-[your-name]/pull/1  
**Final Commit ID:** [Git Commit Hash]  
**Primary Technology Used:** Google Cloud Platform (GCP), Python 3.10+, BigQuery, Dataflow (Apache Beam), GCS, Cloud Composer (Airflow), Vertex AI / Gemini RAG, DuckDB, FastAPI, Terraform  

---

### Solution Summary:
The solution is an enterprise-grade Retail Data Engineering Pipeline & Generative AI Policy Engine built for NorthStar Retail:
1. **Data Engineering (Batch & Streaming)**:
   - Automated ingestion and validation of dirty retail transactions.
   - Master SKU catalog imputation for missing product names, categories, and prices.
   - Medallion Architecture (Bronze -> Silver -> Gold Star Schema) partitioning fact tables by `order_date` and clustering by `store_id` & `product_id`.
   - Separation of gross sales (`fact_orders`) and returns (`fact_returns`).
2. **Generative AI & Policy RAG Assistant**:
   - Vector indexing and retrieval across NorthStar Retail policies: Return Policy (`NSR-POL-RET-014`), Customer Support SLA (`NSR-POL-SUP-005`), Apparel Sizing (`NSR-DOC-SIZ-001`), and Stationery guidelines.
   - Dynamic Tool Calling: Order verification, 30-day return window validation, Grocery exclusion enforcement, 10% restocking fee calculation, and Indian Consumer Protection Act rider compliance.
3. **Dual-Mode Execution (100% Zero-Credential Local Mock + Live GCP)**:
   - Standalone execution without requiring active cloud credentials or paid API keys.
4. **Infrastructure as Code & CI/CD**:
   - Modular Terraform scripts (`gcs.tf`, `bigquery.tf`, `pubsub.tf`, `iam.tf`).
   - GitHub Actions automated CI testing workflow.

### Setup Considerations:
- Default execution is configured in `mock` mode (`EXECUTION_MODE=mock`), enabling immediate out-of-the-box execution and testing without GCP credentials.
- To switch to live cloud execution, update `.env` with `EXECUTION_MODE=gcp` and authenticate via `gcloud auth application-default login`.

### Known Limitations:
- Vertex AI live calls require active quota/credentials; local mock fallback is provided for zero-friction evaluation.
- Dimensions currently implement SCD Type 1; SCD Type 2 can be enabled via Dataform incremental snapshots.

**Reviewer Access Granted:** Yes
