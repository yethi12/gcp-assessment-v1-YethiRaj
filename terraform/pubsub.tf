resource "google_pubsub_topic" "order_events" {
  name = "northstar-order-events-${var.environment}"

  labels = {
    env = var.environment
  }
}

resource "google_pubsub_subscription" "order_events_sub" {
  name  = "northstar-order-events-sub-${var.environment}"
  topic = google_pubsub_topic.order_events.name

  ack_deadline_seconds = 20

  retain_acked_messages = false
  message_retention_duration = "604800s" # 7 days

  expiration_policy {
    ttl = "" # Never expire
  }
}
