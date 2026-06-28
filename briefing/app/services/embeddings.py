"""Sentence-transformer embeddings and FAISS index helpers."""

# Implements ARCH-003, NFR-002

from __future__ import annotations

from typing import TYPE_CHECKING

import faiss
import numpy as np

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer as _ST

_MODEL_NAME = "all-MiniLM-L6-v2"
_model: "_ST | None" = None


def _get_model() -> "_ST":
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def encode(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    arr: np.ndarray = model.encode(texts, convert_to_numpy=True)
    return arr.tolist()


def build_index(vectors: list[list[float]]) -> faiss.IndexFlatIP:
    arr = np.array(vectors, dtype=np.float32)
    faiss.normalize_L2(arr)
    index = faiss.IndexFlatIP(arr.shape[1])
    index.add(arr)
    return index


def search(
    index: faiss.IndexFlatIP,
    query: list[float],
    k: int = 5,
) -> tuple[list[int], list[float]]:
    q = np.array([query], dtype=np.float32)
    faiss.normalize_L2(q)
    distances, indices = index.search(q, k)
    return indices[0].tolist(), distances[0].tolist()
