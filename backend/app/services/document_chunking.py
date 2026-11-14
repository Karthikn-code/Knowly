
"""
Knowly document text chunking service.
"""

import re
from typing import TypedDict


class DocumentChunkData(TypedDict):
    chunk_index: int
    content: str
    source_metadata: dict[str, int]


def split_text_into_chunks(
    text: str,
    chunk_size: int = 3000,
    overlap: int = 400,
) -> list[DocumentChunkData]:
    """Split extracted text into overlapping chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    if not text or not text.strip():
        return []

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    chunks: list[DocumentChunkData] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        hard_end = min(start + chunk_size, text_length)
        end = hard_end

        if hard_end < text_length:
            minimum_boundary = start + int(chunk_size * 0.6)

            paragraph_boundary = text.rfind(
                "\n\n", minimum_boundary, hard_end
            )

            if paragraph_boundary != -1:
                end = paragraph_boundary + 2
            else:
                word_boundary = text.rfind(
                    " ", minimum_boundary, hard_end
                )

                if word_boundary != -1:
                    end = word_boundary

        raw_content = text[start:end]

        left_trim = len(raw_content) - len(raw_content.lstrip())
        right_trim = len(raw_content.rstrip())

        content = raw_content.strip()

        actual_start = start + left_trim
        actual_end = start + right_trim

        if content:
            chunks.append(
                {
                    "chunk_index": len(chunks),
                    "content": content,
                    "source_metadata": {
                        "start_char": actual_start,
                        "end_char": actual_end,
                    },
                }
            )

        if end >= text_length:
            break

        start = max(start + 1, actual_end - overlap)

    return chunks
