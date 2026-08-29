output "landing_bucket" {
  value       = google_storage_bucket.landing_bucket.name
  description = "GCS Landing Zone bucket name"
}

output "processed_bucket" {
  value       = google_storage_bucket.processed_bucket.name
  description = "GCS Processed Zone bucket name"
}

output "bigquery_dataset" {
  value       = google_bigquery_dataset.retail_mart.dataset_id
  description = "BigQuery analytics dataset ID"
}

output "pubsub_topic" {
  value       = google_pubsub_topic.order_events.id
  description = "Pub/Sub orders streaming topic ID"
}
