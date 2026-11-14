
import pytest

from app.services.rag_service import _validate_answer_citations


def make_citation(source_id: str) -> dict:
    return {
        "source_id": source_id,
        "document_id": f"document-{source_id}",
        "chunk_id": f"chunk-{source_id}",
        "filename": f"{source_id}.txt",
        "chunk_index": 0,
        "source_metadata": {},
        "similarity": 0.8,
    }


def test_valid_citations_are_preserved():
    citations = [
        make_citation("S1"),
        make_citation("S2"),
    ]

    answer = "The document explains the process [S1]. It gives an example [S2]."

    cleaned, validated = _validate_answer_citations(
        answer,
        citations,
    )

    assert cleaned == answer
    assert [item["source_id"] for item in validated] == [
        "S1",
        "S2",
    ]


def test_unknown_citation_is_removed():
    citations = [make_citation("S1")]

    answer = "The document explains the process [S1]. Another claim [S99]."

    cleaned, validated = _validate_answer_citations(
        answer,
        citations,
    )

    assert "[S1]" in cleaned
    assert "[S99]" not in cleaned
    assert [item["source_id"] for item in validated] == ["S1"]


def test_malformed_citation_is_removed():
    citations = [make_citation("S1")]

    answer = "The result is supported [S1]. Invalid marker [Sx]."

    cleaned, validated = _validate_answer_citations(
        answer,
        citations,
    )

    assert "[S1]" in cleaned
    assert "[Sx]" not in cleaned
    assert len(validated) == 1


def test_combined_malformed_citation_is_removed():
    citations = [
        make_citation("S1"),
        make_citation("S2"),
    ]

    answer = "The document contains information [S1, S2]."

    cleaned, validated = _validate_answer_citations(
        answer,
        citations,
    )

    assert "[S1, S2]" not in cleaned
    assert validated == []


def test_only_actually_cited_sources_are_returned():
    citations = [
        make_citation("S1"),
        make_citation("S2"),
        make_citation("S3"),
    ]

    answer = "The first source supports this statement [S1]."

    cleaned, validated = _validate_answer_citations(
        answer,
        citations,
    )

    assert cleaned == answer
    assert [item["source_id"] for item in validated] == ["S1"]


def test_repeated_citations_return_metadata_once():
    citations = [
        make_citation("S1"),
        make_citation("S2"),
    ]

    answer = "First point [S1]. Second point [S1]."

    _, validated = _validate_answer_citations(
        answer,
        citations,
    )

    assert [item["source_id"] for item in validated] == ["S1"]


def test_citation_metadata_is_returned_in_source_order():
    citations = [
        make_citation("S1"),
        make_citation("S2"),
        make_citation("S3"),
    ]

    answer = "Third source [S3]. First source [S1]."

    _, validated = _validate_answer_citations(
        answer,
        citations,
    )

    assert [item["source_id"] for item in validated] == [
        "S1",
        "S3",
    ]


def test_no_citations_returns_empty_metadata():
    citations = [make_citation("S1")]

    answer = "The document contains useful information."

    cleaned, validated = _validate_answer_citations(
        answer,
        citations,
    )

    assert cleaned == answer
    assert validated == []


def test_non_string_answer_is_rejected():
    with pytest.raises(TypeError):
        _validate_answer_citations(
            answer=None,
            citations=[],
        )
