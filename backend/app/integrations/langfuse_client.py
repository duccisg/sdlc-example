from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator, Optional

logger = logging.getLogger(__name__)

try:
    from langfuse import Langfuse
except ImportError:  # pragma: no cover - optional dependency
    Langfuse = None  # type: ignore[misc,assignment]
except Exception as exc:  # pragma: no cover - optional dependency
    logger.warning("Langfuse integration disabled due to import failure: %s", exc)
    Langfuse = None  # type: ignore[misc,assignment]

from app.config import Settings


class LangfuseProvider:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Optional[Langfuse] = None

        if Langfuse and settings.langfuse_public_key and settings.langfuse_secret_key:
            self._client = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host,
            )

    @property
    def enabled(self) -> bool:
        return self._client is not None

    @contextmanager
    def trace(self, name: str, metadata: Optional[dict] = None) -> Iterator[None]:
        if not self._client:
            yield
            return

        trace = self._client.trace(name=name, metadata=metadata)
        try:
            yield
        finally:
            trace.end()
