"""
Apache Airflow / Cloud Composer DAG for NorthStar Retail Daily Ingestion & RAG Indexing.
"""
from datetime import datetime, timedelta
from typing import Dict, Any

# Mock Airflow imports if running in lightweight local environment without apache-airflow installed
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.operators.bash import BashOperator
    from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
    from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    DAG = object
    PythonOperator = object
    BashOperator = object

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

def extract_and_clean_task():
    from src.pipeline.cleaner import clean_retail_data
    from src.pipeline.data_transformer import DataTransformer
    from src.config import settings
    import pandas as pd
    
    raw_file = settings.DATA_DIR / "raw" / "orders.csv"
    if raw_file.exists():
        transformer = DataTransformer(settings.PROCESSED_DIR)
        res = transformer.run_pipeline(str(raw_file))
        print(f"Pipeline executed successfully: {res['metrics']}")

def update_vector_index_task():
    from src.agent.rag_engine import PolicyRAGEngine
    from src.config import settings
    engine = PolicyRAGEngine(settings.DATA_DIR / "raw" / "policies.json")
    print(f"Vector RAG index updated with {len(engine.chunks)} policy chunks.")

if AIRFLOW_AVAILABLE:
    with DAG(
        dag_id="northstar_retail_etl_and_rag_dag",
        default_args=default_args,
        description="Daily Retail Dataflow ETL, BigQuery Modeling, and Policy RAG Refresh",
        schedule_interval=timedelta(days=1),
        start_date=datetime(2026, 1, 1),
        catchup=False,
        tags=["retail", "bigquery", "dataflow", "vertex-ai"],
    ) as dag:

        t1 = PythonOperator(
            task_id="extract_clean_transform",
            python_callable=extract_and_clean_task
        )

        t2 = PythonOperator(
            task_id="update_policy_rag_index",
            python_callable=update_vector_index_task
        )

        t1 >> t2
