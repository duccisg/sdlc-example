from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.integrations.langfuse_client import LangfuseProvider
from app.models.workflow import AgentMessage, AgentResult, SDLCPhase, WorkflowState
from app.services.agent_manager import AgentRegistry


@dataclass
class WorkflowConfig:
    registry: AgentRegistry
    langfuse: Optional[LangfuseProvider] = None


class SDLCWorkflowGraph:
    """Internal workflow engine that sequences SDLC agents without langgraph."""

    def __init__(self, config: WorkflowConfig) -> None:
        self._registry = config.registry
        self._langfuse = config.langfuse

    def run(self, state: WorkflowState, *, recursion_limit: int = 50) -> WorkflowState:
        """Advance the workflow until confirmation is required or it completes."""

        current_state = dict(state)
        steps = 0

        while steps < recursion_limit:
            phase = current_state.get("phase")
            if phase is None:
                return current_state

            agent = self._registry.get_agent(phase)
            user_message = current_state.get("user_message")

            if self._langfuse and self._langfuse.enabled:
                context_manager = self._langfuse.trace(
                    name=f"{phase.value}_agent",
                    metadata={
                        "workflow_id": current_state.get("workflow_id"),
                        "phase": phase.value,
                    },
                )
            else:
                context_manager = _nullcontext()

            with context_manager:
                result: AgentResult = agent.run(current_state, user_message)

            message = AgentMessage(
                sender=agent.name,
                phase=phase,
                content=result.output,
                metadata=result.artifacts,
            )

            history = [*current_state.get("history", []), message]
            artifacts = {**current_state.get("artifacts", {}), agent.name: result.artifacts}

            next_state: WorkflowState = {
                "workflow_id": current_state["workflow_id"],
                "history": history,
                "artifacts": artifacts,
                "pending_confirmation": result.requires_confirmation,
                "last_result": result.model_dump(),
                "phase": result.suggested_next_phase,
                "user_message": None,
            }

            current_state = next_state

            if result.requires_confirmation:
                return current_state

            steps += 1

        raise RuntimeError("Workflow recursion limit exceeded")


class _nullcontext:
    def __enter__(self):  # pragma: no cover - trivial
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):  # pragma: no cover - trivial
        return False