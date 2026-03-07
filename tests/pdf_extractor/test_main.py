from unittest.mock import patch
from fastapi.testclient import TestClient
from pdf_extractor.main import app

client = TestClient(app)

def test_webhook_with_filename():
    """Test the webhook endpoint when a filename is provided."""
    payload = {"filename": "pdf/test_document.pdf"}
    
    # We patch run_batch so it doesn't actually execute
    with patch("pdf_extractor.main.run_batch") as mock_run_batch:
        response = client.post("/", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {"status": "accepted", "processing_file": "pdf/test_document.pdf"}
        
        # Verify that BackgroundTasks added run_batch with the correct filename
        # Fastapi TestClient actually executes background tasks synchronously
        mock_run_batch.assert_called_once_with(filename="pdf/test_document.pdf")

def test_webhook_without_filename():
    """Test the webhook endpoint when no filename is provided (full batch)."""
    payload = {}
    
    with patch("pdf_extractor.main.run_batch") as mock_run_batch:
        response = client.post("/", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {"status": "accepted", "processing_file": None}
        
        # Verify run_batch was called with filename=None
        mock_run_batch.assert_called_once_with(filename=None)
