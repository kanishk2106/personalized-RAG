resource "google_secret_manager_secret_iam_member" "r2_access_key_id_reader" {
  secret_id = "projects/${var.project_id}/secrets/r2-access-key-id"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.service_account_email}"
}

resource "google_secret_manager_secret_iam_member" "r2_secret_access_key_reader" {
  secret_id = "projects/${var.project_id}/secrets/r2-secret-access-key"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.service_account_email}"
}