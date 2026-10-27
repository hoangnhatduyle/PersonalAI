import json
import os
import sys

import numpy as np
import pytest
from langchain_core.documents import Document

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rag_index
from rag_index import (
    EMBEDDING_MODEL,
    SimpleVectorStore,
    build_knowledge_base_chunks,
    load_index,
    save_index,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _chunks(n=3):
    return [
        Document(page_content=f"chunk {i}", metadata={"source": f"s{i}.md", "doc_type": "Test"})
        for i in range(n)
    ]


def _vectors(n=3):
    return np.eye(n, dtype=np.float32)


def test_similarity_search_returns_closest_chunk_and_score():
    store = SimpleVectorStore(_chunks(), _vectors(), embed_query=lambda q: [0.0, 1.0, 0.0])

    docs, top_score = store.similarity_search("anything", k=2)

    assert docs[0].page_content == "chunk 1"
    assert len(docs) == 2
    assert top_score == pytest.approx(1.0)


def test_similarity_search_normalizes_stored_vectors():
    vectors = np.array([[10.0, 0.0], [0.0, 0.5]], dtype=np.float32)
    store = SimpleVectorStore(_chunks(2), vectors, embed_query=lambda q: [0.0, 3.0])

    _, top_score = store.similarity_search("q", k=1)

    assert top_score == pytest.approx(1.0)


def test_vector_store_rejects_mismatched_chunk_and_vector_counts():
    with pytest.raises(ValueError):
        SimpleVectorStore(_chunks(3), _vectors(2), embed_query=lambda q: [1.0, 0.0])


def test_save_then_load_round_trips_chunks_and_vectors(tmp_path):
    chunks, vectors = _chunks(), _vectors()

    save_index(chunks, vectors, document_count=2, index_dir=str(tmp_path))
    loaded = load_index(str(tmp_path))

    assert loaded is not None
    assert [c.page_content for c in loaded.chunks] == [c.page_content for c in chunks]
    assert loaded.chunks[1].metadata == chunks[1].metadata
    assert np.array_equal(loaded.vectors, vectors)
    assert loaded.document_count == 2


def test_load_index_returns_none_when_files_missing(tmp_path):
    assert load_index(str(tmp_path)) is None


def test_load_index_returns_none_on_embedding_model_mismatch(tmp_path):
    save_index(_chunks(), _vectors(), document_count=1, index_dir=str(tmp_path))
    meta_path = tmp_path / rag_index.CHUNKS_FILE
    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    payload["embedding_model"] = "some-other-model"
    meta_path.write_text(json.dumps(payload), encoding="utf-8")

    assert load_index(str(tmp_path)) is None


def test_load_index_returns_none_when_vector_count_differs_from_chunks(tmp_path):
    save_index(_chunks(3), _vectors(3), document_count=1, index_dir=str(tmp_path))
    np.save(tmp_path / rag_index.VECTORS_FILE, _vectors(2))

    assert load_index(str(tmp_path)) is None


def test_committed_index_matches_current_knowledge_base():
    """Fails when Knowledge_Base changed but scripts/build_index.py was not re-run."""
    index_dir = os.path.join(REPO_ROOT, rag_index.INDEX_DIR)
    loaded = load_index(index_dir)
    assert loaded is not None, "index/ missing or invalid — run `python scripts/build_index.py`"

    chunks, document_count = build_knowledge_base_chunks(os.path.join(REPO_ROOT, "Knowledge_Base"))

    assert loaded.chunk_fingerprint == rag_index.fingerprint_chunks(chunks), (
        "Knowledge_Base changed since the index was built — run `python scripts/build_index.py`"
    )
    assert loaded.document_count == document_count
    assert EMBEDDING_MODEL == "text-embedding-3-small"
