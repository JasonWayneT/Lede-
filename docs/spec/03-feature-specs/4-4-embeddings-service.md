# Story 4.4: Embeddings Service -- sentence-transformers and FAISS

Status: ready-for-dev

## Story

As a developer,
I want an embeddings service that generates vector embeddings for text chunks and supports FAISS similarity search,
so that the cluster stage can group newsletter excerpts about the same story without LLM calls.

## Acceptance Criteria

1. **Given** a list of text strings, **When** I call `embeddings.encode(texts)`, **Then** a list of float vectors is returned, one per input text, using the configured sentence-transformers model

2. **Given** the embedding service initializing for the first time, **When** the model is not cached locally, **Then** it downloads automatically and caches to the local HuggingFace cache directory

3. **Given** a list of vectors, **When** I call `embeddings.build_index(vectors)`, **Then** a FAISS flat index is created and returned

4. **Given** a FAISS index and a query vector, **When** I call `embeddings.search(index, query_vector, k=5)`, **Then** the k nearest neighbor indices and distances are returned

5. **Given** the embeddings service, **When** I inspect its imports, **Then** it imports `sentence_transformers` and `faiss` — it does not call `llm.complete()` or any LLM provider

## Tasks / Subtasks

- [ ] Implement `app/services/embeddings.py` (AC: 1–5)
  - [ ] `_MODEL_NAME = "all-MiniLM-L6-v2"` — module-level constant (small, fast, good quality for topic clustering)
  - [ ] `_model: SentenceTransformer | None = None` — lazy singleton, loaded on first call
  - [ ] `def _get_model() -> SentenceTransformer`: load `SentenceTransformer(_MODEL_NAME)` if not cached, auto-downloads on first call
  - [ ] `def encode(texts: list[str]) -> list[list[float]]`: call `_get_model().encode(texts, convert_to_numpy=True).tolist()`
  - [ ] `def build_index(vectors: list[list[float]]) -> faiss.IndexFlatIP`: convert to float32 numpy array, `faiss.normalize_L2(arr)`, `index = faiss.IndexFlatIP(arr.shape[1])`, `index.add(arr)`, return index
  - [ ] `def search(index: faiss.IndexFlatIP, query: list[float], k: int = 5) -> tuple[list[int], list[float]]`: normalize query, call `index.search(np.array([query], dtype=np.float32), k)`, return flattened indices and distances

- [ ] Write tests in `tests/services/test_embeddings.py` (AC: 1, 3, 4)
  - [ ] Mock `SentenceTransformer` to avoid downloading model in tests
  - [ ] Test `encode()` returns one vector per input text
  - [ ] Test `build_index()` creates a FAISS index with correct dimension
  - [ ] Test `search()` returns k nearest neighbors

## Dev Notes

### Model choice: all-MiniLM-L6-v2

This 80MB model is fast, CPU-compatible, and well-suited for semantic topic clustering. It is NOT the same as Ollama embeddings (which the architecture explicitly avoids due to known version mismatch issues).

### Inner product vs L2

Use `IndexFlatIP` (inner product) with L2-normalized vectors, which is equivalent to cosine similarity. This is the standard pattern for semantic similarity search with sentence-transformers.

### Lazy loading

Load the model on first call, not at module import time. This avoids 80MB+ load at startup and allows tests to mock the model without actual download.

### sentence-transformers runs synchronously

sentence-transformers is NOT async. Run in a thread pool executor if needed to avoid blocking the event loop during pipeline execution:

```python
import asyncio
loop = asyncio.get_event_loop()
vectors = await loop.run_in_executor(None, _get_model().encode, texts)
```

Or call synchronously from the stage (stages are also called in async context but the executor handles blocking).

### References

- [Source: docs/ARCHITECTURE.md § "Selected Stack — Embeddings, Vector clustering"] — sentence-transformers + FAISS, rationale
- [Source: docs/epics-stories.md § "Story 4.4"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
