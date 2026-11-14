
"""
Knowly - Conversation-Aware Query Contextualization.

Build contextual search queries from recent conversation history
without making an additional Gemini API call.
"""

import re
from collections.abc import Sequence
from typing import Any


MAX_HISTORY_MESSAGES = 4
MAX_MESSAGE_LENGTH = 500
MAX_CONTEXT_LENGTH = 2000
MAX_SHORT_QUESTION_WORDS = 3

FOLLOW_UP_PATTERNS = (
    r"\bit\b",
    r"\bits\b",
    r"\bthey\b",
    r"\bthem\b",
    r"\btheir\b",
    r"\bthose\b",
    r"\bthese\b",
    r"\bthat\b",
    r"\bthis\b",
    r"\bsuch\b",
    r"\bthere\b",
    r"\bmore about\b",
    r"\btell me more\b",
    r"\bwhat about\b",
    r"\bhow about\b",
    r"\bexplain further\b",
    r"\bwhy\b",
    r"\bhow does\b",
    r"\bhow do they\b",
    r"\bwhat technologies\b",
)

FOLLOW_UP_REGEX = re.compile(
    "|".join(FOLLOW_UP_PATTERNS),
    re.IGNORECASE,
)


def _get_valid_history(
    history: Sequence[dict[str, Any]] | None,
) -> list[dict[str, str]]:
    """Extract the most recent valid conversation messages."""

    if not history:
        return []

    valid_messages: list[dict[str, str]] = []

    for message in history[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content")

        if role not in {"user", "assistant"}:
            continue

        if not isinstance(content, str):
            continue

        content = content.strip()

        if not content:
            continue

        valid_messages.append({
            "role": role,
            "content": content[:MAX_MESSAGE_LENGTH],
        })

    return valid_messages


def _is_follow_up_question(question: str) -> bool:
    """Identify questions that probably depend on conversation history."""

    normalized_question = question.strip()

    if not normalized_question:
        return False

    word_count = len(normalized_question.split())

    return (
        bool(FOLLOW_UP_REGEX.search(normalized_question))
        or word_count <= MAX_SHORT_QUESTION_WORDS
    )


def build_contextual_search_query(
    question: str,
    history: Sequence[dict[str, Any]] | None = None,
) -> str:
    """
    Contextualize follow-up questions for semantic retrieval.

    Standalone questions remain unchanged.
    Original question wording is preserved.
    """

    original_question = question.strip()

    if not original_question:
        return original_question

    if not _is_follow_up_question(original_question):
        return original_question

    valid_history = _get_valid_history(history)

    if not valid_history:
        return original_question

    context_parts = [
        f"{message['role']}: {message['content']}"
        for message in valid_history
    ]

    conversation_context = "\n".join(context_parts)
    conversation_context = conversation_context[:MAX_CONTEXT_LENGTH]

    return (
        "Conversation context for understanding the current question:\n"
        f"{conversation_context}\n\n"
        "Current question:\n"
        f"{original_question}"
    )
