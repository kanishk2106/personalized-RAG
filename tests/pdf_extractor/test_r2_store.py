from unittest.mock import MagicMock, patch
from pdf_extractor.r2_store import R2Store
from pdf_extractor.settings import Settings

def test_r2_store_initialization_and_head():
    dummy_settings = Settings(
        r2_account_id="dummy_account",
        r2_access_key_id="dummy_key",
        r2_secret_access_key="dummy_secret",
        bucket="dummy_bucket",
        pdf_prefix="pdf/",
        out_prefix="extracted/",
        min_text_chars_per_page=30,
        ocr_dpi=250,
        ocr_lang="eng",
        language_hint="en"
    )
    with patch("pdf_extractor.r2_store.boto3.client") as mock_boto3_client:
        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3
        store = R2Store(dummy_settings)
        assert store.bucket == "dummy_bucket"
        mock_s3.head_object.return_value = {"ContentLength": 1234}
        resp = store.head("test_key.pdf")
        assert resp["ContentLength"] == 1234
        mock_s3.head_object.assert_called_once_with(Bucket="dummy_bucket", Key="test_key.pdf")
