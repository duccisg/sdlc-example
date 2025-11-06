from __future__ import annotations

from copy import deepcopy
from typing import Dict, Optional
from uuid import uuid4

from langgraph.types import RunnableConfig

from app.models.workflow import SDLCPhase, WorkflowState
from app.workflows.sdlc_graph import SDLCWorkflowGraph


class WorkflowNotFoundError(Exception):
    pass


class InvalidWorkflowTransition(Exception):
    pass


class WorkflowOrchestrator:
    def __init__(self, graph: SDLCWorkflowGraph, recursion_limit: int = 50) -> None:
        self._graph = graph
        self._sessions: Dict[str, WorkflowState] = {}
        self._config = RunnableConfig(recursion_limit=recursion_limit)

    def start(self, initial_message: str) -> WorkflowState:
        workflow_id = str(uuid4())
        initial_state: WorkflowState = {
            "workflow_id": workflow_id,
            "phase": SDLCPhase.INTAKE,
            "history": [],
            "artifacts": {},
            "pending_confirmation": False,
            "last_result": None,
            "user_message": initial_message,
        }

        result = self._graph.app.invoke(initial_state, config=self._config)
        self._sessions[workflow_id] = result
        return result

    def continue_with_confirmation(
        self, workflow_id: str, user_message: Optional[str] = None
    ) -> WorkflowState:
        state = self._get_state(workflow_id)

        if not state.get("pending_confirmation", False):
            raise InvalidWorkflowTransition(
                "Workflow is not awaiting confirmation; cannot advance"
            )

        updated_state = deepcopy(state)
        updated_state["pending_confirmation"] = False
        updated_state["user_message"] = user_message

        result = self._graph.app.invoke(updated_state, config=self._config)
        self._sessions[workflow_id] = result
        return result

    def update_user_message(self, workflow_id: str, user_message: str) -> WorkflowState:
        state = self._get_state(workflow_id)
        updated_state = deepcopy(state)
        updated_state["user_message"] = user_message
        self._sessions[workflow_id] = updated_state
        return updated_state

    def get_state(self, workflow_id: str) -> WorkflowState:
        return deepcopy(self._get_state(workflow_id))

    def _get_state(self, workflow_id: str) -> WorkflowState:
        if workflow_id not in self._sessions:
            raise WorkflowNotFoundError(f"Workflow {workflow_id} not found")
        return self._sessions[workflow_id]
