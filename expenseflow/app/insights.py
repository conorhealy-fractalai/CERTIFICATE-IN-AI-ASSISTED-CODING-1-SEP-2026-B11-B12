"""AI-generated spending insights over stored expenses, via the Anthropic Messages API."""

import json
import logging
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Course material calls this "claude-sonnet-4-6"; using the real current model id
# so the call actually resolves.
MODEL = "claude-sonnet-5"
MAX_TOKENS = 300

SYSTEM_PROMPT = (
    "You are a spending analyst. Respond with JSON only, no prose, no code fences. "
    'The JSON object must have exactly two keys: "summary" (a short string) and '
    '"bullets" (an array of exactly three short strings). '
    "If the expenses span more than one currency, do not sum or average amounts across "
    "differing currencies as if they were equivalent — call out the currency mixture explicitly instead."
)

_FALLBACK: dict = {
    "summary": "Insights are temporarily unavailable.",
    "bullets": [
        "Could not generate an AI summary right now.",
        "Your expense data is unaffected.",
        "Please try again shortly.",
    ],
}


def _build_summary_text(expenses: list[dict]) -> str:
    if not expenses:
        return "No expenses recorded yet."
    lines = [
        f"- {e.get('amount_base_minor', 0) / 100:.2f} {e.get('currency', '?')}, "
        f"category={e.get('category', 'unknown')}, status={e.get('status', 'unknown')}"
        for e in expenses
    ]
    return "Expenses:\n" + "\n".join(lines)


def _strip_code_fence(text: str) -> str:
    """Strip a ```json ... ``` or ``` ... ``` wrapper if the model added one anyway."""
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.removeprefix("```json").removeprefix("```").strip()
        stripped = stripped.removesuffix("```").strip()
    return stripped


def _valid_shape(data: object) -> bool:
    return (
        isinstance(data, dict)
        and isinstance(data.get("summary"), str)
        and isinstance(data.get("bullets"), list)
        and len(data["bullets"]) == 3
        and all(isinstance(b, str) for b in data["bullets"])
    )


def _call_model(expenses: list[dict]) -> dict:
    api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    client = anthropic.Anthropic(api_key=api_key)
    summary_text = _build_summary_text(expenses)

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{summary_text}\n\n"
                    "Give three short bullet insights about this spending."
                ),
            }
        ],
    )
    raw_text = _strip_code_fence(response.content[0].text)
    data = json.loads(raw_text)
    if not _valid_shape(data):
        raise ValueError(f"Unexpected shape from model: {data!r}")
    return data


def generate_insight(expenses: list[dict]) -> dict:
    """Call Claude for a structured spending summary, retrying once on failure.

    Returns a dict with keys "summary" (str) and "bullets" (list[str] of length 3).
    Never raises: on any API, network, or parsing error it returns a safe fallback.
    """
    for attempt in range(2):
        try:
            return _call_model(expenses)
        except Exception as exc:  # noqa: BLE001 - any failure must fall back safely
            logger.warning("generate_insight attempt %d failed: %s", attempt + 1, exc)
    return _FALLBACK
