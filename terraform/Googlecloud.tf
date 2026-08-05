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
resource "google_cloud_run_v2_service" "embedding" {
  name                = "embedding-service"
  location            = var.region
  deletion_protection = true

  template {
    service_account = var.service_account_email
    timeout         = "${var.timeout_seconds}s"

    containers {
      image = var.embedding_image_url

      ports {
        container_port = var.container_port
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
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
        name  = "PINECONE_INDEX"
        value = var.pinecone_index
      }

      env {
        name  = "LOG_LEVEL"
        value = var.log_level
      }

      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = "projects/${var.project_id}/secrets/database-url"
            version = "latest"
          }
        }
      }

      env {
        name = "PINECONE_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "projects/${var.project_id}/secrets/pinecone-api-key"
            version = "latest"
          }
        }
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
resource "google_cloud_run_v2_service" "RAG_Generation" {
  name                = "rag-service"
  location            = var.region
  deletion_protection = false

  template {
    service_account = var.service_account_email
    timeout         = "${var.timeout_seconds}s"

    containers {
      image = var.rag_image_url

      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = "4"
          memory = "4Gi"
        }
      }

      env {
        name  = "PINECONE_INDEX"
        value = var.pinecone_index
      }

      env {
        name  = "LOG_LEVEL"
        value = var.log_level
      }

      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = "projects/${var.project_id}/secrets/database-url"
            version = "latest"
          }
        }
      }

      env {
        name = "Modal_Token_ID"
        value_source {
          secret_key_ref {
            secret  = "projects/${var.project_id}/secrets/modal-token-id"
            version = "latest"
          }
        }
      }

      env {
        name = "Modal_Token_Secret"
        value_source {
          secret_key_ref {
            secret  = "projects/${var.project_id}/secrets/modal-token-secret"
            version = "latest"
          }
        }
      }

      env {
        name = "PINECONE_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "projects/${var.project_id}/secrets/pinecone-api-key"
            version = "latest"
          }
        }
      }

      startup_probe {
        failure_threshold = 1
        period_seconds    = 240
        timeout_seconds   = 240

        tcp_socket {
          port = 8000
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
resource "google_service_account" "rag_invoker" {
  account_id   = "rag-invoker"
  display_name = "RAG Service Invoker Account"
}
resource "google_cloud_run_v2_service_iam_member" "rag_access" {
  name     = google_cloud_run_v2_service.RAG_Generation.name
  location = google_cloud_run_v2_service.RAG_Generation.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.rag_invoker.email}"
}

resource "google_cloud_run_v2_service" "app_server" {
  name                = "rag-app-server"
  location            = var.region
  deletion_protection = false

  template {
    # Must be the invoker SA: it is the only member granted run.invoker on
    # rag-service, and the Node proxy mints its ID token from this identity.
    service_account = google_service_account.rag_invoker.email
    timeout         = "${var.timeout_seconds}s"

    scaling {
      max_instance_count = var.app_server_max_instances
    }

    containers {
      # trimspace: values pasted into GitHub repo variables often carry a
      # trailing newline, which makes the image reference unresolvable.
      image = trimspace(var.app_server_image_url)

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      # Read straight off the RAG service so the URL is never copied by hand.
      env {
        name  = "RAG_SERVICE_URL"
        value = google_cloud_run_v2_service.RAG_Generation.uri
      }

      env {
        name  = "CORS_ORIGIN"
        value = trimspace(var.cors_origin)
      }

      env {
        name  = "RATE_LIMIT_WINDOW_MS"
        value = var.rate_limit_window_ms
      }

      env {
        name  = "RATE_LIMIT_MAX"
        value = var.rate_limit_max
      }
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [google_project_service.run_api]
}

# Browsers reach this service directly, so it is public. The RAG service behind
# it stays private, reachable only via the invoker SA above.
resource "google_cloud_run_v2_service_iam_member" "app_server_public" {
  name     = google_cloud_run_v2_service.app_server.name
  location = google_cloud_run_v2_service.app_server.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}