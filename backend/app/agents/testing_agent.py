from __future__ import annotations

from typing import Optional

from app.agents.base import SDLCBaseAgent
from app.models.workflow import AgentResult, SDLCPhase, WorkflowState


class TestingAgent(SDLCBaseAgent):
    name = "testing"
    phase = SDLCPhase.TESTING
    system_prompt = (
        "You are a QA lead. Devise unit, integration, and functional testing strategies. "
        "Highlight automated test coverage and manual validation steps."
    )

    def build_human_input(
        self, state: WorkflowState, user_message: Optional[str]
    ) -> str:
        history = self.serialize_state_fragment(state)
        return (
            "Implementation context:\n"
            f"{history}\n\n"
            "Testing feedback or constraints:\n"
            f"{user_message or 'No additional constraints.'}"
        )

    def parse_response(self, response, state: WorkflowState) -> AgentResult:
        base = super().parse_response(response, state)
        base.suggested_next_phase = SDLCPhase.DEPLOYMENT
        return base
