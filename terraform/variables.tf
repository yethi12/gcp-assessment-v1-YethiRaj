variable "project_id" {
  type        = string
  description = "Google Cloud Project ID"
  default     = "northstar-retail-dev"
}

variable "region" {
  type        = string
  description = "GCP primary deployment region"
  default     = "asia-south1"
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, staging, prod)"
  default     = "dev"
}

variable "landing_bucket_name" {
  type        = string
  description = "GCS bucket for raw order and policy landing"
  default     = "northstar-retail-landing-zone"
}

variable "processed_bucket_name" {
  type        = string
  description = "GCS bucket for cleaned Parquet outputs"
  default     = "northstar-retail-processed-zone"
}

variable "bigquery_dataset_id" {
  type        = string
  description = "BigQuery dataset ID for data mart"
  default     = "northstar_retail_mart"
}
