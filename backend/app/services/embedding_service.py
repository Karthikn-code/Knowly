
"""
Knowly Gemini embedding service.
"""

import asyncio
import logging
import math

from google import genai
from google.genai import types

from app.core.config import settings


logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768


class GeminiEmbeddingError(Exception):
    """Raised when Gemini embedding generation fails."""


def _generate_embedding_sync(
    text: str,
    task_type: str,
) -> list[float]:
    """Generate a validated embedding using Gemini."""

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Embedding input cannot be empty.")

    api_key = settings.GEMINI_API_KEY.get_secret_value()

    if not api_key:
        raise GeminiEmbeddingError(
            "Gemini API key is not configured."
        )

    client = None

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=EMBEDDING_DIMENSIONS,
            ),
        )

        if not response.embeddings:
            raise GeminiEmbeddingError(
                "Gemini returned an empty embedding response."
            )

        values = response.embeddings[0].values

        if values is None:
            raise GeminiEmbeddingError(
                "Gemini returned an empty vector."
            )

        embedding = [float(value) for value in values]

        if len(embedding) != EMBEDDING_DIMENSIONS:
            raise GeminiEmbeddingError(
                "Gemini returned an unexpected embedding dimension."
            )

        if not all(math.isfinite(value) for value in embedding):
            raise GeminiEmbeddingError(
                "Embedding contains invalid values."
            )

        return embedding

    except GeminiEmbeddingError:
        raise

    except Exception:
        logger.exception(
            "Gemini embedding generation failed. Model: %s",
            EMBEDDING_MODEL,
        )

        raise GeminiEmbeddingError(
            "Gemini embedding generation failed."
        ) from None

    finally:
        if client is not None:
            client.close()


async def generate_document_embedding(text: str) -> list[float]:
    """Generate an embedding for document content."""

    return await asyncio.to_thread(
        _generate_embedding_sync,
        text,
        "RETRIEVAL_DOCUMENT",
    )


async def generate_query_embedding(query: str) -> list[float]:
    """Generate an embedding for a user's search query."""

    return await asyncio.to_thread(
        _generate_embedding_sync,
        query,
        "RETRIEVAL_QUERY",
    )
