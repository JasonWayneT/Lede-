# Story 4.5: Embed and Cluster Stages

Status: ready-for-dev

## Story

As a developer,
I want the embed stage to generate embeddings for extracted texts and the cluster stage to group similar excerpts into story clusters,
so that newsletters covering the same event are collapsed into a single story candidate.

## Acceptance Criteria

1. **Given** a HandoffPacket with `extracted_texts`, **When** the embed stage runs, **Then** it returns the packet with `embeddings` populated — one vector per extracted text entry in the same order

2. **Given** a HandoffPacket with `embeddings`, **When** the cluster stage runs, **Then** it returns the packet with `clusters` populated — each cluster is a list of `extracted_text` entries grouped by similarity

3. **Given** two extracted texts covering the same news event (high cosine similarity), **When** the cluster stage runs, **Then** they appear in the same cluster regardless of which newsletter they came from

4. **Given** two extracted texts covering distinct events, **When** the cluster stage runs, **Then** they appear in different clusters

5. **Given** `AppConfig`, **When** I inspect it, **Then** a `similarity_threshold` setting exists (default `0.75`) that controls cluster granularity

6. **Given** the embed and cluster stages each completing, **When** the orchestrator processes them, **Then** HandoffPackets are written to disk: `stage_03_embed.json` and `stage_04_cluster.json`

## Tasks / Subtasks

- [ ] Implement `app/pipeline/stages/embed.py` (AC: 1, 6)
  - [ ] `async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket`
  - [ ] Extract text strings: `[entry["text"] for entry in packet.extracted_texts]`
  - [ ] Call `embeddings.encode(texts)` — run in executor if needed (see Story 4.4 dev notes)
  - [ ] Assign to `packet.embeddings` — same order as `packet.extracted_texts`
  - [ ] Wrap exceptions in `StageError("embed", str(e), retryable=True)`

- [ ] Implement `app/pipeline/stages/cluster.py` (AC: 2–5, 6)
  - [ ] `async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket`
  - [ ] Build FAISS index: `index = embeddings.build_index(packet.embeddings)`
  - [ ] Greedy clustering: iterate through extracted_texts, for each unassigned item search for neighbors above `config.similarity_threshold`, group them
  - [ ] Each cluster = list of `extracted_text` dicts (not just indices)
  - [ ] Assign to `packet.clusters`
  - [ ] Wrap exceptions in `StageError("cluster", str(e), retryable=True)`

- [ ] Add `similarity_threshold` to `AppConfig` (AC: 5)
  - [ ] Already specified in Story 1.2 dev notes — confirm it is present, default `0.75`

- [ ] Write tests in `tests/pipeline/stages/test_embed.py` and `test_cluster.py` (AC: 1–5)
  - [ ] Mock `embeddings.encode` returning pre-computed float vectors
  - [ ] Test embed: one vector per extracted_text, same order
  - [ ] Test cluster: two high-similarity texts → same cluster; two low-similarity texts → different clusters
  - [ ] Use mock vectors to avoid loading sentence-transformers model in tests

## Dev Notes

### Clustering algorithm

Use greedy nearest-neighbor clustering (not k-means, not DBSCAN — those require knowing k in advance or density parameters that don't map cleanly to the threshold-based AC). Algorithm:

```
assigned = set()
clusters = []
for i, text_entry in enumerate(extracted_texts):
    if i in assigned: continue
    query_vec = embeddings[i]
    indices, distances = embeddings_service.search(index, query_vec, k=len(extracted_texts))
    cluster = [extracted_texts[j] for j, d in zip(indices, distances) if d >= threshold and j not in assigned]
    assigned.update([j for j, d in zip(indices, distances) if d >= threshold])
    clusters.append(cluster)
```

This ensures each text belongs to exactly one cluster (the first one that "claims" it).

### Embeddings in HandoffPacket

`packet.embeddings` is a list of lists (not numpy arrays) after deserialization. Convert to numpy in the cluster stage: `np.array(packet.embeddings, dtype=np.float32)`.

### Stage order in orchestrator

Orchestrator calls stages in this order: ingest → extract → embed → cluster → select → frame → draft → tts_prep → assemble → qa_gate. Embed is stage 3, cluster is stage 4 (but artifact numbering includes the ingest=01, extract=02, embed=03, cluster=04 pattern).

### References

- [Source: docs/ARCHITECTURE.md § "Pipeline Stage Interface"] — stage signature
- [Source: docs/ARCHITECTURE.md § "Structure Patterns — Handoff Artifact Files"] — `stage_03_embed.json`, `stage_04_cluster.json`
- [Source: docs/epics-stories.md § "Story 4.5"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
