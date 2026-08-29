resource "google_bigquery_dataset" "retail_mart" {
  dataset_id                  = var.bigquery_dataset_id
  friendly_name               = "NorthStar Retail Mart"
  description                 = "Analytical mart containing bronze, silver, and gold dimensional tables"
  location                    = var.region
  default_table_expiration_ms = null

  labels = {
    env      = var.environment
    domain   = "retail-analytics"
    pipeline = "northstar-etl"
  }
}

resource "google_bigquery_table" "fact_orders" {
  dataset_id = google_bigquery_dataset.retail_mart.dataset_id
  table_id   = "fact_orders"

  time_partitioning {
    type  = "DAY"
    field = "order_date"
  }

  clustering = ["store_id", "product_id"]

  schema = <<EOF
[
  {"name": "order_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "date_key", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "order_date", "type": "DATE", "mode": "REQUIRED"},
  {"name": "store_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "product_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "quantity", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "unit_price", "type": "FLOAT", "mode": "REQUIRED"},
  {"name": "total_amount", "type": "FLOAT", "mode": "REQUIRED"}
]
EOF
}

resource "google_bigquery_table" "fact_returns" {
  dataset_id = google_bigquery_dataset.retail_mart.dataset_id
  table_id   = "fact_returns"

  time_partitioning {
    type  = "DAY"
    field = "order_date"
  }

  clustering = ["store_id", "product_id"]

  schema = <<EOF
[
  {"name": "order_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "date_key", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "order_date", "type": "DATE", "mode": "REQUIRED"},
  {"name": "store_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "product_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "quantity_returned", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "unit_price", "type": "FLOAT", "mode": "REQUIRED"},
  {"name": "refund_amount", "type": "FLOAT", "mode": "REQUIRED"}
]
EOF
}
