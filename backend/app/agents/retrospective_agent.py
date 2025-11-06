from __future__ import annotations

from typing import Optional

from app.agents.base import SDLCBaseAgent
from app.models.workflow import AgentResult, SDLCPhase, WorkflowState


class RetrospectiveAgent(SDLCBaseAgent):
    name = "retrospective"
    phase = SDLCPhase.RETROSPECTIVE
    system_prompt = (
        "You are an agile coach. Summarize the overall engagement, highlight successes, "
        "lessons learned, and recommendations for future iterations."
    )

    def build_human_input(
        self, state: WorkflowState, user_message: Optional[str]
    ) -> str:
        history = self.serialize_state_fragment(state)
        return (
            "Full workflow context:\n"
            f"{history}\n\n"
            "Stakeholder feedback for retrospective:\n"
            f"{user_message or 'No additional feedback provided.'}"
        )

    def parse_response(self, response, state: WorkflowState) -> AgentResult:
        base = super().parse_response(response, state)
        base.suggested_next_phase = None
        base.requires_confirmation = False
        return base
