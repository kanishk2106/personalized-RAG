from unittest.mock import MagicMock, patch
from pdf_extractor.pipeline import process_one_pdf
from pdf_extractor.settings import Settings
from pdf_extractor.extract import ExtractionResult


def test_process_one_pdf_success():
    """Minimal test to verify the end-to-end pipeline orchestration with mocks."""
    
    # Create dummy settings
    dummy_settings = Settings(
        r2_account_id="dummy",
        r2_access_key_id="dummy",
        r2_secret_access_key="dummy",
        bucket="dummy",
        pdf_prefix="pdf/",
        out_prefix="extracted/",
    )

    # Mock the R2Store instance
    mock_store = MagicMock()
    mock_store.bucket = "dummy_bucket"
    mock_store.head.return_value = {"ContentLength": 1024}
    mock_store.get_bytes.return_value = b"fake_pdf_data"

    # Mock the extraction result
    mock_extraction_result = ExtractionResult(
        pages=[{"page": 1, "text": "Extracted text", "char_count": 14}],
        scanned_suspected=False,
        stats={"page_count": 1, "total_chars": 14, "empty_page_count": 0}
    )

    # Patch the actual extraction function to avoid doing real PDF processing
    with patch("pdf_extractor.pipeline.extract_text_with_fallback", return_value=mock_extraction_result):
        # Patch datetime to have a predictable timestamp if we ever wanted to assert on it
        with patch("pdf_extractor.pipeline.datetime") as mock_datetime:
             mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00Z"

             # Run the pipeline function for one PDF
             process_one_pdf(mock_store, dummy_settings, "pdf/test_doc.pdf")

    # Assert that the store methods were called correctly
    mock_store.head.assert_called_once_with("pdf/test_doc.pdf")
    mock_store.get_bytes.assert_called_once_with("pdf/test_doc.pdf")
    mock_store.put_json.assert_called_once()
    
    # Assert that put_json was called with the correct output key structure
    put_args, _ = mock_store.put_json.call_args
    assert put_args[0] == "extracted/test_doc.json"
    
    # You can also inspect the json payload to ensure schema structure is generated correctly
    output_dict = put_args[1]
    assert output_dict["doc"]["pdf"]["r2_key"] == "pdf/test_doc.pdf"
    assert output_dict["extraction"]["scanned_suspected"] is False
    assert len(output_dict["pages"]) == 1
