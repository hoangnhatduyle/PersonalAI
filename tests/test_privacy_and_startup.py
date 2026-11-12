"""Privacy guards (immigration details stay out of everything the chatbot can see or show), UI
guards (no review badge), consistency guards, and the no-OpenAI-at-startup behaviour."""

import glob
import json
import os
import re
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import rag_index  # noqa: E402

KB = os.path.join(REPO_ROOT, "Knowledge_Base")

# Documents use Unicode hyphens (e.g. "EB\u20112"), so every hyphen is a character class.
_H = "[-\u2010-\u2015\u2212]?"
IMMIGRATION = re.compile(
    rf"visa|h{_H}1b|stem[\s\u2010-\u2015-]opt|\bopt\b|\bcpt\b|\bf{_H}1\b|eb{_H}2|\bniw\b"
    rf"|green card|immigration|work authori[sz]ation|lottery|\bi{_H}20\b|uscis"
    rf"|national interest waiver|sponsorship",
    re.IGNORECASE,
)


def _read(path):
    with open(os.path.join(REPO_ROOT, path), encoding="utf-8") as f:
        return f.read()


def _kb_markdown():
    for path in sorted(glob.glob(os.path.join(KB, "**", "*.md"), recursive=True)):
        with open(path, encoding="utf-8") as f:
            yield os.path.relpath(path, REPO_ROOT), f.read()


# --- immigration details are not visible to the chatbot --------------------------------------


def test_no_immigration_details_in_any_knowledge_base_document():
    offenders = {}
    for path, text in _kb_markdown():
        hits = sorted({m.group(0).lower() for m in IMMIGRATION.finditer(text)})
        if hits:
            offenders[path] = hits
    assert offenders == {}


def test_no_immigration_details_in_the_precomputed_index():
    with open(os.path.join(REPO_ROOT, "index", "chunks.json"), encoding="utf-8") as f:
        payload = json.load(f)
    leaking = [
        c["metadata"].get("source", "?")
        for c in payload["chunks"]
        if IMMIGRATION.search(c["page_content"])
    ]
    assert leaking == []


def test_summary_loaded_into_the_system_prompt_has_no_immigration_details():
    text = _read("me/summary.txt")
    assert not IMMIGRATION.search(text)


def test_summary_describes_the_current_situation():
    text = _read("me/summary.txt")
    assert "University of Cincinnati" in text
    assert "CincySI" in text


def test_profile_card_shows_no_visa_status():
    card = _read("frontend/components/ProfileCard.tsx")
    assert not IMMIGRATION.search(card)


def test_topic_classifier_does_not_route_on_immigration_keywords():
    app = _read("app.py")
    classifier = app.split("def _classify_topic", 1)[1].split("def _generate_suggestions", 1)[0]
    assert not IMMIGRATION.search(classifier)


def test_system_prompt_declines_immigration_questions():
    """With the facts removed, the assistant must decline rather than guess."""
    app = _read("app.py").lower()
    rule4 = app.split("4. never disclose sensitive", 1)[1].split("5. if the visitor wants", 1)[0]
    assert "immigration" in rule4 and "work-authorization" in rule4.replace(" ", "-")


# --- the annual review badge is gone from the UI ---------------------------------------------


def test_profile_card_has_no_annual_review_badge():
    card = _read("frontend/components/ProfileCard.tsx").lower()
    assert "annual review" not in card
    assert "rated" not in card


# --- consistency with the portfolio ------------------------------------------------------------


def test_experience_is_stated_as_four_plus_years_not_three():
    for path, text in _kb_markdown():
        assert "3+ years" not in text, f"{path} still says 3+ years"
    assert "4+ years" in _read("Knowledge_Base/Background/professional_summary.md")


def test_gpa_is_consistently_3_89():
    text = _read("Knowledge_Base/Background/professional_summary.md")
    assert "3.89" in text
    assert "3.90" not in text


# --- startup does not reach out to GitHub/OpenAI when the precomputed index is usable ------------


def _fake_index():
    return rag_index.LoadedIndex(chunks=[], vectors=[], document_count=0, chunk_fingerprint="x")


def test_github_docs_are_not_fetched_when_a_precomputed_index_loads():
    assert rag_index.github_docs_needed(_fake_index()) is False


def test_github_docs_are_fetched_only_for_the_embedding_fallback():
    assert rag_index.github_docs_needed(None) is True


def test_app_startup_routes_through_the_seam():
    app = _read("app.py")
    init = app.split("def __init__(self):", 1)[1].split("# ── GitHub Integration", 1)[0]
    assert "github_docs_needed(" in init
    assert "self._initialize_rag(loaded)" in init


def test_the_committed_index_loads_without_any_network_call():
    loaded = rag_index.load_index(os.path.join(REPO_ROOT, "index"))
    assert loaded is not None and len(loaded.chunks) > 0


@pytest.mark.parametrize("path", ["Knowledge_Base/Work Experience/role_5_CincySI_Lab.md"])
def test_knowledge_base_documents_are_not_gitignored(path):
    import subprocess

    result = subprocess.run(
        ["git", "check-ignore", "-q", path], cwd=REPO_ROOT, capture_output=True
    )
    assert result.returncode == 1, f"{path} is gitignored and would never be deployed"
