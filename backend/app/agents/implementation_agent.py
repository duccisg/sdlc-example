from __future__ import annotations

from typing import Optional

from app.agents.base import SDLCBaseAgent
from app.models.workflow import AgentResult, SDLCPhase, WorkflowState


class ImplementationAgent(SDLCBaseAgent):
    name = "implementation"
    phase = SDLCPhase.IMPLEMENTATION
    system_prompt = (
        "You are a senior software engineer. Produce implementation guidance including "
        "code scaffolding, libraries to use, and best practices for maintainability."
    )

    def build_human_input(
        self, state: WorkflowState, user_message: Optional[str]
    ) -> str:
        history = self.serialize_state_fragment(state)
        return (
            "Design blueprint and context:\n"
            f"{history}\n\n"
            "Specific implementation request:\n"
            f"{user_message or 'No additional requests.'}"
        )

    def parse_response(self, response, state: WorkflowState) -> AgentResult:
        base = super().parse_response(response, state)
        base.suggested_next_phase = SDLCPhase.TESTING
        return base
