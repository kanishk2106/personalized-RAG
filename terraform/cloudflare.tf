resource "cloudflare_r2_bucket" "rag_data" {
  account_id = var.cloudflare_account_id
  name       = var.r2_bucket_name
}

resource "cloudflare_queue" "pdf_jobs" {
  account_id = var.cloudflare_account_id
  queue_name = var.queue_name
}

resource "cloudflare_r2_bucket_event_notification" "pdf_trigger" {
  account_id  = var.cloudflare_account_id
  bucket_name = cloudflare_r2_bucket.rag_data.name
  queue_id    = cloudflare_queue.pdf_jobs.id

  rules = [{
    actions = ["PutObject"]
    prefix  = var.r2_pdf_prefix
  }]
}