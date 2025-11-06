from __future__ import annotations

from typing import List, Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - optional dependency
    ChatOpenAI = None  # type: ignore

from app.config import Settings


def create_default_llm(settings: Settings, responses: Optional[list[str]] = None) -> BaseChatModel:
    """Return a chat model based on available credentials.

    If OpenAI credentials are available, use ChatOpenAI. Otherwise fall back to a
    deterministic fake LLM useful for local development and testing.
    """

    if settings.openai_api_key and ChatOpenAI is not None:
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=settings.openai_api_key,
        )

    # Fallback deterministic model for offline development
    default_message = (
        responses[0]
        if responses
        else "Stub response. Configure OPENAI_API_KEY to enable full LLM output."
    )
    return StubChatModel(message=default_message)


class StubChatModel(BaseChatModel):
    def __init__(self, message: str):
        super().__init__()
        self._message = message

    @property
    def _llm_type(self) -> str:  # pragma: no cover - metadata
        return "stub-chat-model"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> ChatResult:
        message = AIMessage(content=self._message)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])
