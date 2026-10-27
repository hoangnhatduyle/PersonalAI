"""
Build the precomputed RAG index from Knowledge_Base/*.md.

Run from the repo root whenever the Knowledge_Base changes, then commit index/:

    python scripts/build_index.py

This is the only place chunk embeddings are computed, so production cold
starts need no OpenAI call to boot.
"""

import os
import sys

import numpy as np
from dotenv import load_dotenv

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from langchain_openai import OpenAIEmbeddings  # noqa: E402

import rag_index  # noqa: E402


def main() -> None:
    os.chdir(REPO_ROOT)
    load_dotenv(override=True)
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY not set (.env or environment)")

    chunks, document_count = rag_index.build_knowledge_base_chunks("Knowledge_Base")
    print(f"Chunked {document_count} documents into {len(chunks)} chunks — embedding...")

    embeddings = OpenAIEmbeddings(model=rag_index.EMBEDDING_MODEL)
    vectors = np.array(
        embeddings.embed_documents([c.page_content for c in chunks]),
        dtype=np.float32,
    )

    rag_index.save_index(chunks, vectors, document_count)
    print(f"Wrote {rag_index.INDEX_DIR}/ ({len(chunks)} vectors, dim {vectors.shape[1]})")


if __name__ == "__main__":
    main()
