from unittest.mock import patch
from pdf_extractor.extract import extract_text_with_fallback, ExtractionResult

def test_extract_text_with_fallback_success():
    mock_pages = [
        {"page": 1, "text": "Hello World", "char_count": 11},
        {"page": 2, "text": "Test Page 2", "char_count": 11}
    ]
    
    with patch("pdf_extractor.extract.extract_with_pdfplumber", return_value=mock_pages):
        result = extract_text_with_fallback(
            pdf_bytes=b"dummy_pdf_content",
            min_text_chars_per_page=10,
            ocr_dpi=300,
            ocr_lang="eng"
        )
        
        assert isinstance(result, ExtractionResult)
        assert len(result.pages) == 2
        assert result.pages[0]["text"] == "Hello World"
        assert result.stats["page_count"] == 2
        assert result.stats["total_chars"] == 22
