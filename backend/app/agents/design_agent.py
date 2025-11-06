from __future__ import annotations

from typing import Optional

from app.agents.base import SDLCBaseAgent
from app.models.workflow import AgentResult, SDLCPhase, WorkflowState


class SolutionDesignAgent(SDLCBaseAgent):
    name = "solution_design"
    phase = SDLCPhase.DESIGN
    system_prompt = (
        "You are a software designer. Produce a high-level design including "
        "component diagram narrative, data model sketches, and API contracts. "
        "Tailor the solution to the preferred tech stack when specified."
    )

    def build_human_input(
        self, state: WorkflowState, user_message: Optional[str]
    ) -> str:
        history = self.serialize_state_fragment(state)
        return (
            "Requirements and analysis summary:\n"
            f"{history}\n\n"
            "Design considerations from user:\n"
            f"{user_message or 'No additional design considerations.'}"
        )

    def parse_response(self, response, state: WorkflowState) -> AgentResult:
        base = super().parse_response(response, state)
        base.suggested_next_phase = SDLCPhase.IMPLEMENTATION
        return base
