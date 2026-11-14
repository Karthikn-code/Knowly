
import pytest

from app.services.document_chunking import split_text_into_chunks


def test_empty_text_returns_no_chunks():
    assert split_text_into_chunks("") == []


def test_whitespace_only_text_returns_no_chunks():
    assert split_text_into_chunks("   \n\n   ") == []


def test_short_text_returns_one_chunk():
    text = "Knowly is an AI document assistant."

    chunks = split_text_into_chunks(text)

    assert len(chunks) == 1
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["content"] == text
    assert chunks[0]["source_metadata"] == {
        "start_char": 0,
        "end_char": len(text),
    }


def test_chunks_preserve_original_text_content():
    text = (
        "First paragraph contains useful information.\n\n"
        "Second paragraph contains more information.\n\n"
        "Third paragraph completes the document."
    )

    chunks = split_text_into_chunks(
        text,
        chunk_size=60,
        overlap=10,
    )

    assert len(chunks) > 1

    for chunk in chunks:
        metadata = chunk["source_metadata"]

        assert chunk["content"] == text[
            metadata["start_char"]:metadata["end_char"]
        ]


def test_chunk_indices_are_sequential():
    text = " ".join(
        f"word{i}" for i in range(100)
    )

    chunks = split_text_into_chunks(
        text,
        chunk_size=80,
        overlap=15,
    )

    assert [
        chunk["chunk_index"] for chunk in chunks
    ] == list(range(len(chunks)))


def test_chunk_metadata_offsets_are_valid():
    text = " ".join(
        f"word{i}" for i in range(100)
    )

    chunks = split_text_into_chunks(
        text,
        chunk_size=80,
        overlap=15,
    )

    for chunk in chunks:
        start = chunk["source_metadata"]["start_char"]
        end = chunk["source_metadata"]["end_char"]

        assert 0 <= start < end <= len(text)
        assert chunk["content"] == text[start:end]


def test_chunks_have_overlap():
    text = " ".join(
        f"word{i}" for i in range(100)
    )

    chunks = split_text_into_chunks(
        text,
        chunk_size=80,
        overlap=15,
    )

    assert len(chunks) > 1

    for previous, current in zip(chunks, chunks[1:]):
        previous_end = previous["source_metadata"]["end_char"]
        current_start = current["source_metadata"]["start_char"]

        assert current_start < previous_end


def test_newlines_are_normalized():
    text = "First paragraph.\r\n\r\n\r\nSecond paragraph."

    chunks = split_text_into_chunks(text)

    assert len(chunks) == 1
    assert chunks[0]["content"] == (
        "First paragraph.\n\nSecond paragraph."
    )


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [
        (0, 0),
        (-1, 0),
        (100, -1),
        (100, 100),
        (100, 101),
    ],
)
def test_invalid_chunk_configuration_raises_error(
    chunk_size,
    overlap,
):
    with pytest.raises(ValueError):
        split_text_into_chunks(
            "Some document text.",
            chunk_size=chunk_size,
            overlap=overlap,
        )


def test_long_text_is_split_into_multiple_chunks():
    text = " ".join(
        f"word{i}" for i in range(1000)
    )

    chunks = split_text_into_chunks(
        text,
        chunk_size=300,
        overlap=40,
    )

    assert len(chunks) > 1
    assert all(chunk["content"] for chunk in chunks)
    assert all(
        len(chunk["content"]) <= 300
        for chunk in chunks
    )
