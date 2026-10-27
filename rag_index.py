"""
Knowledge-base indexing for the RAG pipeline.

Chunking, the in-memory vector store, and the on-disk index format live here
(not in app.py) so scripts/build_index.py and the tests can use them without
importing app.py, which constructs PersonalAI() and calls OpenAI at import time.
"""

import glob
import hashlib
import json
import os
from dataclasses import dataclass
from typing import Callable

import numpy as np
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

INDEX_DIR = "index"
VECTORS_FILE = "chunk_vectors.npy"
CHUNKS_FILE = "chunks.json"


# ─────────────────────────────────────────────
# Loading + chunking
# ─────────────────────────────────────────────
def load_markdown_dir(folder: str, doc_type: str) -> list[Document]:
    """Load all *.md files under folder as Documents."""
    docs = []
    for path in sorted(glob.glob(os.path.join(folder, "**", "*.md"), recursive=True)):
        with open(path, "r", encoding="utf-8") as f:
            docs.append(Document(
                page_content=f.read(),
                metadata={"source": path, "doc_type": doc_type},
            ))
    return docs


def load_knowledge_base_docs(kb_path: str) -> list[Document]:
    """Load every Knowledge_Base subfolder, using the folder name as doc_type."""
    docs = []
    for folder in sorted(glob.glob(os.path.join(kb_path, "*"))):
        if os.path.isdir(folder):
            docs.extend(load_markdown_dir(folder, os.path.basename(folder)))
    return docs


def chunk_documents(
    docs: list[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """Two-pass chunking: heading-aware, then size-aware."""
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
        strip_headers=False,
    )
    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = []
    for doc in docs:
        try:
            header_docs = []
            for split in header_splitter.split_text(doc.page_content):
                merged_meta = {**doc.metadata}
                for key in ("h1", "h2", "h3"):
                    if key in split.metadata:
                        merged_meta[key] = split.metadata[key]
                header_docs.append(Document(
                    page_content=split.page_content,
                    metadata=merged_meta,
                ))
            chunks.extend(size_splitter.split_documents(header_docs))
        except Exception:
            # Fallback: just size-split the whole document
            chunks.extend(size_splitter.split_documents([doc]))
    return chunks


def build_knowledge_base_chunks(kb_path: str) -> tuple[list[Document], int]:
    """Chunk the Knowledge_Base. Returns (chunks, number of source documents)."""
    docs = load_knowledge_base_docs(kb_path)
    return chunk_documents(docs), len(docs)


def fingerprint_chunks(chunks: list[Document]) -> str:
    """Stable hash of chunk texts, used to detect a stale index."""
    digest = hashlib.sha256()
    for chunk in chunks:
        digest.update(chunk.page_content.encode("utf-8"))
        digest.update(b"\x00")
    return digest.hexdigest()


# ─────────────────────────────────────────────
# Lightweight in-memory vector store
#
# The knowledge base is a few hundred chunks. A numpy cosine-similarity scan
# does the same job as Chroma without the onnxruntime/kubernetes/grpc
# dependency chain, which is what pushed the Vercel function past its 500MB
# bundle limit. Chunk vectors are precomputed by scripts/build_index.py;
# only the query is embedded at request time.
# ─────────────────────────────────────────────
class SimpleVectorStore:
    def __init__(
        self,
        chunks: list[Document],
        vectors: np.ndarray,
        embed_query: Callable[[str], list[float]],
    ):
        if len(chunks) != len(vectors):
            raise ValueError(
                f"chunk/vector count mismatch: {len(chunks)} chunks, {len(vectors)} vectors"
            )
        self._chunks = chunks
        self._embed_query = embed_query
        vectors = np.asarray(vectors, dtype=np.float32)
        self._normalized = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    def similarity_search(self, query: str, k: int) -> tuple[list[Document], float]:
        """Returns the top-k chunks plus the best cosine similarity score, so callers can tell whether anything actually relevant was found."""
        query_vec = np.array(self._embed_query(query), dtype=np.float32)
        query_vec /= np.linalg.norm(query_vec)
        scores = self._normalized @ query_vec
        top_k = np.argsort(-scores)[:k]
        top_score = float(scores[top_k[0]]) if len(top_k) else 0.0
        return [self._chunks[i] for i in top_k], top_score


class SimpleRetriever:
    def __init__(self, store: SimpleVectorStore, k: int):
        self._store = store
        self._k = k

    def invoke(self, query: str, k: int | None = None) -> tuple[list[Document], float]:
        return self._store.similarity_search(query, k or self._k)


# ─────────────────────────────────────────────
# On-disk index
# ─────────────────────────────────────────────
@dataclass(frozen=True)
class LoadedIndex:
    chunks: list[Document]
    vectors: np.ndarray
    document_count: int
    chunk_fingerprint: str


def save_index(
    chunks: list[Document],
    vectors: np.ndarray,
    document_count: int,
    index_dir: str = INDEX_DIR,
) -> None:
    if len(chunks) != len(vectors):
        raise ValueError(
            f"chunk/vector count mismatch: {len(chunks)} chunks, {len(vectors)} vectors"
        )
    os.makedirs(index_dir, exist_ok=True)
    np.save(os.path.join(index_dir, VECTORS_FILE), np.asarray(vectors, dtype=np.float32))
    payload = {
        "embedding_model": EMBEDDING_MODEL,
        "document_count": document_count,
        "chunk_fingerprint": fingerprint_chunks(chunks),
        "chunks": [
            {"page_content": c.page_content, "metadata": c.metadata} for c in chunks
        ],
    }
    with open(os.path.join(index_dir, CHUNKS_FILE), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)


def load_index(index_dir: str = INDEX_DIR) -> LoadedIndex | None:
    """Load the precomputed index, or None if it is missing, unreadable, or incompatible."""
    vectors_path = os.path.join(index_dir, VECTORS_FILE)
    chunks_path = os.path.join(index_dir, CHUNKS_FILE)
    if not (os.path.exists(vectors_path) and os.path.exists(chunks_path)):
        return None
    try:
        with open(chunks_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        vectors = np.load(vectors_path)
        if payload["embedding_model"] != EMBEDDING_MODEL:
            print(f"  ⚠ Index built with {payload['embedding_model']}, expected {EMBEDDING_MODEL}")
            return None
        chunks = [
            Document(page_content=c["page_content"], metadata=c["metadata"])
            for c in payload["chunks"]
        ]
        if len(chunks) != len(vectors):
            print(f"  ⚠ Index corrupt: {len(chunks)} chunks vs {len(vectors)} vectors")
            return None
        return LoadedIndex(
            chunks=chunks,
            vectors=vectors,
            document_count=int(payload["document_count"]),
            chunk_fingerprint=payload["chunk_fingerprint"],
        )
    except (OSError, ValueError, KeyError) as e:
        print(f"  ⚠ Could not read index: {e}")
        return None
