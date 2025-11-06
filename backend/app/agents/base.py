from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from app.models.workflow import AgentResult, SDLCPhase, WorkflowState


class SDLCBaseAgent(ABC):
    name: str
    phase: SDLCPhase
    system_prompt: str

    def __init__(self, llm: BaseChatModel) -> None:
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content="{input}"),
            ]
        )

    @abstractmethod
    def build_human_input(self, state: WorkflowState, user_message: Optional[str]) -> str:
        ...

    def run(self, state: WorkflowState, user_message: Optional[str]) -> AgentResult:
        human_input = self.build_human_input(state, user_message)
        chain = self.prompt | self.llm
        response: AIMessage = chain.invoke({"input": human_input})
        return self.parse_response(response, state)

    def parse_response(self, response: AIMessage, state: WorkflowState) -> AgentResult:
        return AgentResult(
            agent=self.name,
            phase=self.phase,
            output=response.content,
            artifacts={
                "raw": response.content,
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
