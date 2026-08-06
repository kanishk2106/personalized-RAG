variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "service_name" {
  type    = string
  default = "pdf-processor"
}

variable "service_account_email" {
  type = string
}

variable "image_url" {
  type = string
}

variable "container_port" {
  type    = number
  default = 8080
}

variable "timeout_seconds" {
  type    = number
  default = 300
}

variable "cpu_limit" {
  type    = string
  default = "1"
}

variable "memory_limit" {
  type    = string
  default = "1Gi"
}

variable "cloudflare_account_id" {
  type = string
}

variable "r2_bucket_name" {
  type    = string
  default = "my-rag-data"
}

variable "queue_name" {
  type    = string
  default = "pdf-jobs"
}

variable "embedding_queue_name" {
  type    = string
  default = "embedding-jobs"
}

variable "r2_pdf_prefix" {
  type    = string
  default = "Advanced NLP/"
}

variable "r2_extract_prefix" {
  type    = string
  default = "extracted-json/"
}

variable "min_text_chars_per_page" {
  type    = number
  default = 30
}

variable "ocr_dpi" {
  type    = number
  default = 250
}

variable "ocr_lang" {
  type    = string
  default = "eng"
}

variable "language_hint" {
  type    = string
  default = "en"
}

variable "log_level" {
  type    = string
  default = "INFO"
}
variable "embedding_image_url" {
  type = string
}
variable "pinecone_index" {
  type    = string
  default = "rag"
}
variable "rag_image_url" {
  type = string
}

variable "app_server_image_url" {
  type = string
}

variable "cors_origin" {
  type    = string
  default = "http://localhost:5173"
}

variable "app_server_max_instances" {
  type    = number
  default = 5
}

variable "rate_limit_window_ms" {
  type    = string
  default = "60000"
}

# 40/min leaves headroom above the client's warmup retry rate (one attempt every
# 3s = 20/min), so a retrying tab cannot exhaust its own budget during an outage.
variable "rate_limit_max" {
  type    = string
  default = "40"
}