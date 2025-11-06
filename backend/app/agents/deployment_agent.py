from __future__ import annotations

from typing import Optional

from app.agents.base import SDLCBaseAgent
from app.models.workflow import AgentResult, SDLCPhase, WorkflowState


class DeploymentAgent(SDLCBaseAgent):
    name = "deployment"
    phase = SDLCPhase.DEPLOYMENT
    system_prompt = (
        "You are a DevOps engineer. Provide a deployment and release plan covering "
        "infrastructure requirements, CI/CD pipeline steps, observability, and rollback strategy."
    )

    def build_human_input(
        self, state: WorkflowState, user_message: Optional[str]
    ) -> str:
        history = self.serialize_state_fragment(state)
        return (
            "Testing outcomes and context:\n"
            f"{history}\n\n"
            "Deployment constraints:\n"
            f"{user_message or 'No additional constraints.'}"
        )

    def parse_response(self, response, state: WorkflowState) -> AgentResult:
        base = super().parse_response(response, state)
        base.suggested_next_phase = SDLCPhase.RETROSPECTIVE
        return base
