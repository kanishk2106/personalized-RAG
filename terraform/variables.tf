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