"""Tests for embeddings service — Story 4.4."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.services import embeddings as emb


def test_encode_returns_one_vector_per_text():
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)

    with patch("app.services.embeddings._get_model", return_value=mock_model):
        result = emb.encode(["text one", "text two"])

    assert len(result) == 2
    assert len(result[0]) == 2
    assert isinstance(result[0][0], float)


def test_build_index_correct_dimension():
    vectors = [[0.1, 0.0, 0.0], [0.0, 1.0, 0.0]]
    index = emb.build_index(vectors)
    assert index.d == 3
    assert index.ntotal == 2


def test_search_returns_k_neighbors():
    vectors = [[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]]
    index = emb.build_index(vectors)
    indices, distances = emb.search(index, [1.0, 0.0], k=2)
    assert len(indices) == 2
    assert len(distances) == 2
    assert 0 in indices


def test_lazy_model_load():
    import app.services.embeddings as emb_mod
    original = emb_mod._model
    emb_mod._model = None
    try:
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1]], dtype=np.float32)
        with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
            result = emb.encode(["test"])
        assert len(result) == 1
    finally:
        emb_mod._model = original
