"""Guards for the research content in the knowledge base, the retrieval index, and the chat UI.

The papers are under double-blind review, so the public chat may say they exist and what they are
about, but must never reveal titles, benchmark names, or results. The forbidden phrases are stored as
SHA-256 hashes of normalized word windows so this (publicly visible) test does not reveal them.
"""

import glob
import hashlib
import json
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB = os.path.join(REPO_ROOT, "Knowledge_Base")

# {word_count: {sha256 of the lowercase, space-joined word sequence}}
FORBIDDEN_HASHES = {
    5: {"e05fbe06d4803e57a41013d42c263226523ad828d49e2a3b48e2479051aa6db2"},
    4: {
        "fb8e78c3c16447c6710e6bd9bac9cae174f18068949d08d05ae6087f16a57f18",
        "0089f45d444c140fafb493a4656d9d1ca50d409df8c725708e2621b804c53bce",
    },
    2: {"38be7c361df00cf24b74594d5f998debe8233d4cd16520d24ebbc3ce824d3fc6"},
    1: {
        "aabf4623354bc44d907b992a3a3cd809d4a7fdd3f03ec540742c38edec02a43c",
        "10807f7425d719577ccf4ae42357e0069f59e648021e44096407f312a5285062",
    },
}


def _read(path):
    with open(os.path.join(REPO_ROOT, path), encoding="utf-8") as f:
        return f.read()


def _kb_markdown():
    for path in sorted(glob.glob(os.path.join(KB, "**", "*.md"), recursive=True)):
        with open(path, encoding="utf-8") as f:
            yield os.path.relpath(path, REPO_ROOT), f.read()


def _contains_forbidden(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    for size, hashes in FORBIDDEN_HASHES.items():
        for i in range(len(words) - size + 1):
            if hashlib.sha256(" ".join(words[i : i + size]).encode()).hexdigest() in hashes:
                return True
    return False


def _kb_text():
    return "\n".join(text for _, text in _kb_markdown())


# --- the knowledge base covers current research -------------------------------------------------


def test_knowledge_base_covers_cincysi_lab_and_advisor():
    text = _kb_text()
    assert "CincySI" in text
    assert "Justin Zhan" in text


def test_a_dedicated_cincysi_role_document_exists():
    matches = glob.glob(os.path.join(KB, "Work Experience", "*CincySI*.md"))
    assert matches, "expected a Work Experience document for the CincySI Lab role"
    text = open(matches[0], encoding="utf-8").read()
    assert "October 2026" in text
    assert "multi-agent" in text.lower()


def test_publications_document_is_not_stale():
    text = _read("Knowledge_Base/Publication_Research/publications.md")
    assert "no formal publications" not in text.lower()
    assert "under review" in text.lower()
    assert "NAACL 2027" in text


def test_masters_document_mentions_the_research_lab():
    assert "CincySI" in _read("Knowledge_Base/Education/masters_degree.md")


# --- the papers stay anonymous --------------------------------------------------------------------


def test_no_forbidden_paper_phrase_in_any_knowledge_base_file():
    leaks = [path for path, text in _kb_markdown() if _contains_forbidden(text)]
    assert leaks == []


def test_assistant_is_told_to_withhold_titles_while_under_review():
    text = _read("Knowledge_Base/Publication_Research/publications.md").lower()
    assert "do not share" in text and "title" in text


# --- the precomputed retrieval index matches the knowledge base -----------------------------------


def _index_chunks():
    with open(os.path.join(REPO_ROOT, "index", "chunks.json"), encoding="utf-8") as f:
        data = json.load(f)
    return data["chunks"] if isinstance(data, dict) else data


def _chunk_text(chunk):
    if isinstance(chunk, str):
        return chunk
    return chunk.get("page_content") or chunk.get("text") or json.dumps(chunk)


def test_index_contains_the_new_research_content():
    assert any("CincySI" in _chunk_text(c) for c in _index_chunks())


def test_index_has_no_forbidden_paper_phrase():
    assert not any(_contains_forbidden(_chunk_text(c)) for c in _index_chunks())


def test_index_is_fresh_for_the_current_knowledge_base():
    """Fails if Knowledge_Base changed without re-running scripts/build_index.py."""
    import rag_index

    chunks, _ = rag_index.build_knowledge_base_chunks(KB)
    loaded = rag_index.load_index(os.path.join(REPO_ROOT, "index"))
    assert loaded is not None, "index/ could not be loaded (stale fingerprint?)"
    assert len(loaded.chunks) == len(chunks)


# --- chat UI and prompt ---------------------------------------------------------------------------


def test_starter_chips_drop_the_annual_review_and_add_a_research_question():
    chips = _read("frontend/components/StarterQuestions.tsx")
    assert "annual review" not in chips.lower()
    assert "research" in chips.lower()


def test_annual_review_questions_can_still_be_answered():
    """Removing the chip must not remove the behaviour: the prompt rule stays."""
    app = _read("app.py")
    assert 'For "annual review" / "performance review" questions' in app
