resource "google_project_service" "run_api" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager_api" {
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_cloud_run_v2_service" "pdf_processor" {
  name                = var.service_name
  location            = var.region
  deletion_protection = true

  template {
    service_account = var.service_account_email
    timeout         = "${var.timeout_seconds}s"

    containers {
      image = var.image_url

      ports {
        container_port = var.container_port
      }

      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
      }

      env {
        name  = "R2_ACCOUNT_ID"
        value = var.cloudflare_account_id
      }

      env {
        name  = "R2_BUCKET_NAME"
        value = var.r2_bucket_name
      }

      env {
        name  = "R2_PDF_PREFIX"
        value = var.r2_pdf_prefix
      }

      env {
        name  = "R2_EXTRACT_PREFIX"
        value = var.r2_extract_prefix
      }

      env {
        name  = "MIN_TEXT_CHARS_PER_PAGE"
        value = tostring(var.min_text_chars_per_page)
      }

      env {
        name  = "OCR_DPI"
        value = tostring(var.ocr_dpi)
      }

      env {
        name  = "OCR_LANG"
        value = var.ocr_lang
      }

      env {
        name  = "LANGUAGE_HINT"
        value = var.language_hint
      }

      env {
        name  = "LOG_LEVEL"
        value = var.log_level
      }

      env {
        name = "R2_ACCESS_KEY_ID"
        value_source {
          secret_key_ref {
            secret  = "projects/${var.project_id}/secrets/r2-access-key-id"
            version = "latest"
          }
        }
      }

      env {
        name = "R2_SECRET_ACCESS_KEY"
        value_source {
          secret_key_ref {
            secret  = "projects/${var.project_id}/secrets/r2-secret-access-key"
            version = "latest"
          }
        }
      }

      startup_probe {
        failure_threshold = 1
        period_seconds    = 240
        timeout_seconds   = 240

        tcp_socket {
          port = var.container_port
        }
      }
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [
    google_project_service.run_api,
    google_project_service.secretmanager_api
  ]
}