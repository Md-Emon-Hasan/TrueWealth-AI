from unittest.mock import MagicMock, patch

import app.tools.vector_store as vector_store
from app.tools.vector_store import (CachedEmbeddings, get_embeddings,
                                    get_memory_store, get_retriever,
                                    setup_vector_store)


def test_vector_store_getters():
    vector_store._embeddings_singleton = None
    with patch('app.tools.vector_store.HuggingFaceEmbeddings') as mock_emb:
        get_embeddings()
        mock_emb.assert_called_once()


def test_get_embeddings_reuses_singleton_across_calls():
    vector_store._embeddings_singleton = None
    with patch('app.tools.vector_store.HuggingFaceEmbeddings') as mock_emb:
        first = get_embeddings()
        second = get_embeddings()
        assert first is second
        mock_emb.assert_called_once()

    with patch('app.tools.vector_store.Chroma') as mock_chroma:
        with patch('app.tools.vector_store.get_embeddings'):
            with patch('os.path.exists', return_value=True):
                with patch('os.listdir', return_value=['index']):
                    setup_vector_store()
                    mock_chroma.assert_called_once()


def test_cached_embeddings_embed_query_caches():
    inner = MagicMock()
    inner.embed_query.return_value = [0.1, 0.2]
    wrapped = CachedEmbeddings(inner)

    wrapped.embed_query("hello")
    wrapped.embed_query("hello")

    inner.embed_query.assert_called_once()


def test_cached_embeddings_embed_documents_passthrough():
    inner = MagicMock()
    inner.embed_documents.return_value = [[0.1], [0.2]]
    wrapped = CachedEmbeddings(inner)

    result = wrapped.embed_documents(["a", "b"])

    assert result == [[0.1], [0.2]]
    inner.embed_documents.assert_called_once_with(["a", "b"])


def test_get_memory_store_uses_separate_collection():
    with patch('app.tools.vector_store.Chroma') as mock_chroma:
        with patch('app.tools.vector_store.get_embeddings'):
            get_memory_store()
            _, kwargs = mock_chroma.call_args
            assert kwargs['collection_name'] == 'conversation_memory'


def test_get_retriever():
    with patch('app.tools.vector_store.setup_vector_store') as mock_setup:
        mock_instance = MagicMock()
        mock_setup.return_value = mock_instance
        get_retriever()
        mock_instance.as_retriever.assert_called_once()


def test_create_new_vectorstore():
    with patch('app.tools.vector_store.Chroma') as mock_chroma:
        with patch('app.tools.document_loader.load_documents', return_value=["Doc"]):
            with patch('app.tools.document_loader.split_documents', return_value=["Split"]):
                with patch('os.makedirs'):
                    with patch('os.path.exists', return_value=True):
                        with patch('os.listdir', return_value=[]):
                            with patch('app.tools.vector_store.PDF_PATH', 'fake.pdf'):
                                from app.tools.vector_store import \
                                    create_new_vectorstore
                                create_new_vectorstore(MagicMock(), 'path')
                                mock_chroma.from_documents.assert_called_once()


def test_setup_vector_store_missing():
    # Test path where vector store doesn't exist
    with patch('app.tools.vector_store.get_embeddings'):
        with patch('os.path.exists', return_value=False):
            with patch('app.tools.vector_store.create_new_vectorstore') as mock_create:
                setup_vector_store()
                mock_create.assert_called_once()


def test_setup_vector_store_error():
    # Test path where vector store load fails
    with patch('app.tools.vector_store.get_embeddings'):
        with patch('os.path.exists', return_value=True):
            with patch('os.listdir', return_value=['index']):
                with patch('app.tools.vector_store.Chroma', side_effect=Exception("Load error")):
                    with patch('app.tools.vector_store.create_new_vectorstore') as mock_create:
                        setup_vector_store()
                        mock_create.assert_called_once()


def test_create_new_vectorstore_no_pdf():
    # Test path where PDF is missing
    with patch('app.tools.vector_store.Chroma') as mock_chroma:
        with patch('os.path.exists', return_value=False):
            with patch('app.tools.vector_store.PDF_PATH', 'missing.pdf'):
                from app.tools.vector_store import create_new_vectorstore
                create_new_vectorstore(MagicMock(), 'path')
                # Should create store WITHOUT from_documents
                mock_chroma.assert_called_once()
                mock_chroma.from_documents.assert_not_called()
