from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.models.workflow import AgentResult, SDLCPhase, WorkflowState
from app.utils.llm import BaseChatModel


class SDLCBaseAgent(ABC):
    name: str
    phase: SDLCPhase
    system_prompt: str

    def __init__(self, llm: BaseChatModel) -> None:
        self.llm = llm

    @abstractmethod
    def build_human_input(self, state: WorkflowState, user_message: Optional[str]) -> str:
        ...

    def run(self, state: WorkflowState, user_message: Optional[str]) -> AgentResult:
        human_input = self.build_human_input(state, user_message)
        response_text = self.llm.generate(self.system_prompt, human_input)
        return self.parse_response(response_text, state)

    def parse_response(self, response_text: str, state: WorkflowState) -> AgentResult:
        return AgentResult(
            agent=self.name,
            phase=self.phase,
            output=response_text,
            artifacts={
                "raw": response_text,
            },
            requires_confirmation=True,
        )

    def serialize_state_fragment(self, state: WorkflowState) -> str:
        history_fragments = []
        for message in state.get("history", [])[-5:]:
            history_fragments.append(
                f"[{message.phase}] {message.sender}: {message.content}"
            )
        artifacts = state.get("artifacts", {})
        return "\n".join(history_fragments) + "\nCurrent artifacts: " + str(artifacts)
