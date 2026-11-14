
"""
Knowly Gemini generation service.
"""

import asyncio
import logging

from google import genai

from app.core.config import settings


logger = logging.getLogger(__name__)


class GeminiGenerationError(Exception):
    """Raised when Gemini response generation fails."""


def _generate_response_sync(prompt: str) -> str:
    """Generate a response using the configured Gemini model."""

    if not prompt or not prompt.strip():
        raise ValueError("Gemini prompt cannot be empty.")

    api_key = settings.GEMINI_API_KEY.get_secret_value()

    if not api_key:
        raise RuntimeError("Gemini API key is not configured.")

    client = genai.Client(api_key=api_key)

    try:
        try:
            response = client.interactions.create(
                model=settings.GEMINI_GENERATION_MODEL,
                input=prompt,
            )
        except Exception:
            logger.exception(
                "Gemini generation request failed. Model: %s",
                settings.GEMINI_GENERATION_MODEL,
            )

            raise GeminiGenerationError(
                "Gemini generation request failed."
            ) from None

        answer = response.output_text

        if not answer or not answer.strip():
            logger.error(
                "Gemini returned an empty response. Model: %s",
                settings.GEMINI_GENERATION_MODEL,
            )

            raise GeminiGenerationError(
                "Gemini returned an empty response."
            )

        return answer.strip()

    finally:
        client.close()


async def generate_response(prompt: str) -> str:
    """Generate a response without blocking the event loop."""

    return await asyncio.to_thread(
        _generate_response_sync,
        prompt,
    )
