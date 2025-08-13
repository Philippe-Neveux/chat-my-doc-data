import pytest
import polars as pl
from unittest.mock import Mock, patch, MagicMock
from qdrant_client import models
from sentence_transformers import SentenceTransformer

from chat_my_doc_data.push_doc_to_db import (
    load_reviews_data,
    encode_reviews,
    add_index,
    Qdrant
)


class TestLoadReviewsData:
    @patch('chat_my_doc_data.push_doc_to_db.pl.read_parquet')
    def test_load_reviews_data_success(self, mock_read_parquet):
        mock_df = pl.DataFrame({
            "review": ["Great movie!", "Not so good"],
            "rating": [5, 2]
        })
        mock_read_parquet.return_value = mock_df
        
        result = load_reviews_data()
        
        mock_read_parquet.assert_called_once_with("gs://rag-open-data/imdb/standard/imdb_reviews.parquet")
        assert result.equals(mock_df)


class TestEncodeReviews:
    def test_encode_reviews_success(self):
        df = pl.DataFrame({
            "review": ["Great movie!", "Not so good"],
            "rating": [5, 2]
        })
        mock_encoder = Mock(spec=SentenceTransformer)
        mock_encoder.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]
        
        result = encode_reviews(df, "review", mock_encoder)
        
        mock_encoder.encode.assert_called_once_with(["Great movie!", "Not so good"])
        assert "vector" in result.columns
        assert result.shape[0] == 2


class TestAddIndex:
    def test_add_index_success(self):
        df = pl.DataFrame({
            "review": ["Great movie!", "Not so good"],
            "rating": [5, 2]
        })
        
        result = add_index(df, "id")
        
        assert "id" in result.columns
        assert result["id"].to_list() == [0, 1]
        assert result.shape[0] == 2


class TestQdrant:
    def setup_method(self):
        self.mock_client = Mock()
        
    @patch('chat_my_doc_data.push_doc_to_db.QdrantClient')
    def test_qdrant_init(self, mock_qdrant_client):
        mock_qdrant_client.return_value = self.mock_client
        
        qdrant = Qdrant("http://localhost:6333")
        
        mock_qdrant_client.assert_called_once_with(url="http://localhost:6333")
        assert qdrant.client == self.mock_client

    @patch('chat_my_doc_data.push_doc_to_db.QdrantClient')
    def test_if_collection_exists_true(self, mock_qdrant_client):
        mock_collection = Mock()
        mock_collection.name = "existing_collection"
        mock_collections = Mock()
        mock_collections.collections = [mock_collection]
        self.mock_client.get_collections.return_value = mock_collections
        mock_qdrant_client.return_value = self.mock_client
        
        qdrant = Qdrant("http://localhost:6333")
        
        result = qdrant._if_collection_exists("existing_collection")
        
        assert result is True

    @patch('chat_my_doc_data.push_doc_to_db.QdrantClient')
    def test_if_collection_exists_false(self, mock_qdrant_client):
        mock_collection = Mock()
        mock_collection.name = "other_collection"
        mock_collections = Mock()
        mock_collections.collections = [mock_collection]
        self.mock_client.get_collections.return_value = mock_collections
        mock_qdrant_client.return_value = self.mock_client
        
        qdrant = Qdrant("http://localhost:6333")
        
        result = qdrant._if_collection_exists("non_existing_collection")
        
        assert result is False

    @patch('chat_my_doc_data.push_doc_to_db.QdrantClient')
    def test_setup_collection_existing(self, mock_qdrant_client):
        mock_collection = Mock()
        mock_collection.name = "existing_collection"
        mock_collections = Mock()
        mock_collections.collections = [mock_collection]
        self.mock_client.get_collections.return_value = mock_collections
        mock_qdrant_client.return_value = self.mock_client
        
        qdrant = Qdrant("http://localhost:6333")
        
        qdrant.setup_collection("existing_collection")
        
        assert qdrant.collection_name == "existing_collection"
        self.mock_client.create_collection.assert_not_called()

    @patch('chat_my_doc_data.push_doc_to_db.QdrantClient')
    def test_setup_collection_new(self, mock_qdrant_client):
        mock_collections = Mock()
        mock_collections.collections = []
        self.mock_client.get_collections.return_value = mock_collections
        mock_qdrant_client.return_value = self.mock_client
        
        qdrant = Qdrant("http://localhost:6333")
        
        qdrant.setup_collection("new_collection", vectors_size=384)
        
        assert qdrant.collection_name == "new_collection"
        self.mock_client.create_collection.assert_called_once()

    @patch('chat_my_doc_data.push_doc_to_db.QdrantClient')
    def test_setup_collection_new_without_vectors_size(self, mock_qdrant_client):
        mock_collections = Mock()
        mock_collections.collections = []
        self.mock_client.get_collections.return_value = mock_collections
        mock_qdrant_client.return_value = self.mock_client
        
        qdrant = Qdrant("http://localhost:6333")

        with pytest.raises(ValueError, match="vectors_size must be specified"):
            qdrant.setup_collection("new_collection")

    @patch('chat_my_doc_data.push_doc_to_db.QdrantClient')
    def test_upload_documents_success(self, mock_qdrant_client):
        mock_qdrant_client.return_value = self.mock_client
        qdrant = Qdrant("http://localhost:6333")
        qdrant.collection_name = "test_collection"
        
        df = pl.DataFrame({
            "id": [0, 1],
            "review": ["Great!", "Bad"],
            "vector": [[0.1, 0.2], [0.3, 0.4]]
        })
        
        qdrant.upload_documents(
            df=df,
            vectors_column="vector",
            id_column="id",
            payload_columns=["review"]
        )
        
        self.mock_client.upload_collection.assert_called_once()

    @patch('chat_my_doc_data.push_doc_to_db.QdrantClient')
    def test_upload_documents_no_collection(self, mock_qdrant_client):
        mock_qdrant_client.return_value = self.mock_client
        qdrant = Qdrant("http://localhost:6333")
        # Don't set collection_name to test the error case
        
        df = pl.DataFrame({"id": [0], "review": ["Great!"]})

        with pytest.raises(AttributeError):
            qdrant.upload_documents(
                df=df,
                vectors_column="vector",
                id_column="id",
                payload_columns=["review"]
            )