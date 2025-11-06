from __future__ import annotations

from typing import Optional

from app.agents.base import SDLCBaseAgent
from app.models.workflow import AgentResult, SDLCPhase, WorkflowState


class RequirementIntakeAgent(SDLCBaseAgent):
    name = "requirement_intake"
    phase = SDLCPhase.INTAKE
    system_prompt = (
        "You are a business analyst specializing in capturing software requirements. "
        "Summarize the user's goals, functional requirements, non-functional criteria, "
        "and any constraints. Ask clarifying questions when information is missing."
    )

    def build_human_input(
        self, state: WorkflowState, user_message: Optional[str]
    ) -> str:
        history = self.serialize_state_fragment(state)
        return (
            "Context so far:\n"
            f"{history}\n\n"
            "New stakeholder input:\n"
            f"{user_message or 'No new message provided.'}"
        )

    def parse_response(self, response, state: WorkflowState) -> AgentResult:
        base = super().parse_response(response, state)
        base.suggested_next_phase = SDLCPhase.ANALYSIS
        return base
