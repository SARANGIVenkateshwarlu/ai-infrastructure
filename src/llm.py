"""
LLM Helper — PROVIDED (do not modify).

Calls a free model on OpenRouter. Usage:

    from llm import call_llm
    response = call_llm(
        system_prompt="You are a helpful assistant.",
        user_message="Classify this intent: ..."
    )
"""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "deepseek/deepseek-v4-flash:free"

# Maximum retries for rate-limited requests (free tier has strict limits)
MAX_RETRIES = 3


def call_llm(
    system_prompt: str,
    user_message: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> str:
    """
    Send a chat completion request to OpenRouter and return the response text.

    Automatically retries on rate-limit (429) errors with backoff.

    Args:
        system_prompt: The system/instruction message.
        user_message: The user message to process.
        model: OpenRouter model identifier. Defaults to a free model.
        temperature: Sampling temperature (0.0-1.0). Lower = more deterministic.
        max_tokens: Maximum tokens in the response.

    Returns:
        str: The model's response text.

    Raises:
        ValueError: If OPENROUTER_API_KEY is not set.
        RuntimeError: If the API call fails after retries.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY not set. "
            "Copy .env.example to .env and add your key from https://openrouter.ai/"
        )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    for attempt in range(MAX_RETRIES + 1):
        resp = requests.post(
            OPENROUTER_URL, headers=headers, json=payload, timeout=60
        )

        if resp.status_code == 200:
            data = resp.json()
            msg = data["choices"][0]["message"]
            # Some models return None content with reasoning in a separate field
            content = msg.get("content") or ""
            return content

        if resp.status_code == 429 and attempt < MAX_RETRIES:
            # Rate limited — wait and retry
            retry_after = 10 * (attempt + 1)
            try:
                error_data = resp.json()
                retry_after = (
                    error_data.get("error", {})
                    .get("metadata", {})
                    .get("retry_after_seconds", retry_after)
                )
            except Exception:
                pass
            time.sleep(min(retry_after + 1, 30))
            continue

        raise RuntimeError(
            f"OpenRouter API error {resp.status_code}: {resp.text}"
        )

    raise RuntimeError("Max retries exceeded for OpenRouter API call")
