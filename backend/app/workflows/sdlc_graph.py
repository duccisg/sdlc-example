from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from langgraph.graph import END, START, StateGraph

from app.integrations.langfuse_client import LangfuseProvider
from app.models.workflow import AgentMessage, AgentResult, SDLCPhase, WorkflowState
from app.services.agent_manager import AgentRegistry


@dataclass
class WorkflowConfig:
    registry: AgentRegistry
    langfuse: Optional[LangfuseProvider] = None


class SDLCWorkflowGraph:
    def __init__(self, config: WorkflowConfig) -> None:
        self._registry = config.registry
        self._langfuse = config.langfuse
        self._graph = StateGraph(WorkflowState)
        self._phase_names = [phase.value for phase in SDLCPhase]
        self._build_graph()

    def _build_graph(self) -> None:
        for phase in SDLCPhase:
            self._graph.add_node(phase.value, self._make_phase_node(phase))
            self._graph.add_conditional_edges(
                phase.value,
                self._route_from_phase,
                self._route_map(),
            )

        self._graph.add_node("await_confirmation", self._await_confirmation)
        self._graph.add_conditional_edges(
            "await_confirmation",
            self._route_after_confirmation,
            self._route_map(),
        )

        self._graph.add_edge(START, SDLCPhase.INTAKE.value)
        self._compiled = self._graph.compile()

    def _route_map(self) -> Dict[str, str]:
        mapping = {phase_name: phase_name for phase_name in self._phase_names}
        mapping["await_confirmation"] = "await_confirmation"
        mapping["end"] = END
        return mapping

    def _make_phase_node(self, phase: SDLCPhase):
        agent = self._registry.get_agent(phase)

        def node(state: WorkflowState) -> WorkflowState:
            user_message = state.get("user_message")

            if self._langfuse and self._langfuse.enabled:
                context_manager = self._langfuse.trace(
                    name=f"{phase.value}_agent",
                    metadata={
                        "workflow_id": state.get("workflow_id"),
                        "phase": phase.value,
                    },
                )
            else:
                context_manager = _nullcontext()

            with context_manager:
                result: AgentResult = agent.run(state, user_message)

            message = AgentMessage(
                sender=agent.name,
                phase=phase,
                content=result.output,
                metadata=result.artifacts,
            )

            history = [*state.get("history", []), message]
            artifacts = {**state.get("artifacts", {}), agent.name: result.artifacts}

            next_phase = result.suggested_next_phase
            return {
                "history": history,
                "artifacts": artifacts,
                "pending_confirmation": result.requires_confirmation,
                "last_result": result.model_dump(),
                "phase": next_phase,
                "user_message": None,
                "workflow_id": state.get("workflow_id"),
            }

        return node

    def _await_confirmation(self, state: WorkflowState) -> WorkflowState:
        return state

    def _route_from_phase(self, state: WorkflowState) -> str:
        if state.get("pending_confirmation", False):
            return "await_confirmation"

        next_phase = state.get("phase")
        if next_phase is None:
            return "end"
        return next_phase.value

    def _route_after_confirmation(self, state: WorkflowState) -> str:
        if state.get("pending_confirmation", False):
            return "await_confirmation"

        next_phase = state.get("phase")
        if next_phase is None:
            return "end"
        return next_phase.value

    @property
    def app(self):
        return self._compiled


class _nullcontext:
    def __enter__(self):  # pragma: no cover - trivial
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):  # pragma: no cover - trivial
        return False
