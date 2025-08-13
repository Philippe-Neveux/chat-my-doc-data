import pytest
import polars as pl
from unittest.mock import Mock


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing."""
    return pl.DataFrame({
        "review": ["Great movie!", "Not so good", "Amazing!"],
        "rating": [5, 2, 4],
        "title": ["Movie A", "Movie B", "Movie C"]
    })


@pytest.fixture
def sample_dataframe_with_vectors():
    """Sample DataFrame with vectors for testing."""
    return pl.DataFrame({
        "id": [0, 1, 2],
        "review": ["Great movie!", "Not so good", "Amazing!"],
        "rating": [5, 2, 4],
        "vector": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
    })


@pytest.fixture
def mock_encoder():
    """Mock SentenceTransformer encoder."""
    encoder = Mock()
    encoder.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
    encoder.get_sentence_embedding_dimension.return_value = 3
    return encoder