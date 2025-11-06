from __future__ import annotations

from typing import Optional

from app.agents.base import SDLCBaseAgent
from app.models.workflow import AgentResult, SDLCPhase, WorkflowState


class SolutionAnalysisAgent(SDLCBaseAgent):
    name = "solution_analysis"
    phase = SDLCPhase.ANALYSIS
    system_prompt = (
        "You are a solution architect. Analyze gathered requirements and outline "
        "key domain concepts, risks, and architectural decisions. Recommend the "
        "target architecture style and integration points."
    )

    def build_human_input(
        self, state: WorkflowState, user_message: Optional[str]
    ) -> str:
        history = self.serialize_state_fragment(state)
        return (
            "Prior context and requirements:\n"
            f"{history}\n\n"
            "Additional analyst notes:\n"
            f"{user_message or 'No additional notes provided.'}"
        )

    def parse_response(self, response, state: WorkflowState) -> AgentResult:
        base = super().parse_response(response, state)
        base.suggested_next_phase = SDLCPhase.DESIGN
        return base
