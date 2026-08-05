output "app_server_url" {
  description = "Public URL of the Node proxy; set this as VITE_API_BASE in Vercel."
  value       = google_cloud_run_v2_service.app_server.uri
}

output "rag_service_url" {
  description = "Private URL of the RAG service (invoker SA only)."
  value       = google_cloud_run_v2_service.RAG_Generation.uri
}
