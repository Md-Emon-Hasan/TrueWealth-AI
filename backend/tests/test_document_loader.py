from unittest.mock import MagicMock, patch

from app.tools.document_loader import load_documents, split_documents


def test_document_loader_with_path():
    with patch('app.tools.document_loader.PyPDFLoader') as mock_loader:
        mock_instance = MagicMock()
        mock_instance.load.return_value = ["Doc1"]
        mock_loader.return_value = mock_instance
        docs = load_documents("dummy.pdf")
        assert docs == ["Doc1"]


def test_document_loader_default_path():
    with patch('app.tools.document_loader.PyPDFLoader') as mock_loader:
        mock_instance = MagicMock()
        mock_instance.load.return_value = ["DefaultDoc"]
        mock_loader.return_value = mock_instance
        # This will trigger 'if not pdf_path'
        docs = load_documents()
        assert docs == ["DefaultDoc"]


def test_split_documents():
    with patch('app.tools.document_loader.RecursiveCharacterTextSplitter') as mock_splitter:
        mock_instance = MagicMock()
        mock_instance.split_documents.return_value = ["Split1"]
        mock_splitter.from_tiktoken_encoder.return_value = mock_instance
        docs = [MagicMock(page_content="Doc1")]
        splits = split_documents(docs)
        assert splits == ["Split1"]
