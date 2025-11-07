from __future__ import annotations

from typing import Optional, Protocol

import httpx

from app.config import Settings


class BaseChatModel(Protocol):
    """Minimal protocol for chat-based language models used by the agents."""

    def generate(self, system_prompt: str, user_input: str) -> str:
        ...


class OpenAIChatModel:
    """Lightweight OpenAI Chat Completions client based on httpx."""

    def __init__(
        self,
        api_key: str,
        *,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._temperature = temperature
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def generate(self, system_prompt: str, user_input: str) -> str:
        """Call the OpenAI Chat Completions API and return the assistant message."""

        payload = {
            "model": self._model,
            "temperature": self._temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = httpx.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - network failure
            raise RuntimeError("Failed to call OpenAI Chat Completions API") from exc

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("OpenAI response did not include any choices")

        message = choices[0].get("message") or {}
        content = message.get("content")
        if content is None:
            raise RuntimeError("OpenAI response choice did not include message content")

        return content.strip()


class StubChatModel:
    """Deterministic chat model useful for local development and tests."""

    def __init__(
        self,
        *,
        default_message: str,
        responses: Optional[list[str]] = None,
    ) -> None:
        self._default_message = default_message
        self._responses = list(responses or [])

    def generate(self, system_prompt: str, user_input: str) -> str:  # noqa: D401
        if self._responses:
            return self._responses.pop(0)
        return self._default_message


def create_default_llm(settings: Settings, responses: Optional[list[str]] = None) -> BaseChatModel:
    """Return a chat model based on available credentials.

    If OpenAI credentials are available, use the real API client. Otherwise fall back to
    a deterministic fake LLM useful for local development and testing.
    """

    if settings.openai_api_key:
        return OpenAIChatModel(
            api_key=settings.openai_api_key,
            model="gpt-4o-mini",
            temperature=0.3,
        )

    responses_queue = list(responses or [])
    default_message = (
        responses_queue[0]
        if responses_queue
        else "Stub response. Configure OPENAI_API_KEY to enable full LLM output."
    )
    return StubChatModel(default_message=default_message, responses=responses_queue)
