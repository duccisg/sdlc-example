from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.workflow import AgentMessage, SDLCPhase, WorkflowState


class StartWorkflowRequest(BaseModel):
    prompt: str = Field(..., description="Initial input such as requirements or goals")


class ContinueWorkflowRequest(BaseModel):
    message: Optional[str] = Field(
        default=None,
        description="Optional additional context provided before the next phase runs",
    )


class AgentMessageView(BaseModel):
    sender: str
    phase: SDLCPhase
    content: str
    metadata: Dict[str, Any]

    @classmethod
    def from_model(cls, message: AgentMessage) -> "AgentMessageView":
        return cls(
            sender=message.sender,
            phase=message.phase,
            content=message.content,
            metadata=message.metadata,
        )


class AgentResultView(BaseModel):
    agent: str
    phase: SDLCPhase
    output: str
    artifacts: Dict[str, Any]
    requires_confirmation: bool
    suggested_next_phase: Optional[SDLCPhase]

    @classmethod
    def from_payload(cls, payload: Optional[Dict[str, Any]]) -> Optional["AgentResultView"]:
        if payload is None:
            return None
        return cls.model_validate(payload)


class WorkflowStateView(BaseModel):
    workflow_id: str
    current_phase: Optional[SDLCPhase]
    pending_confirmation: bool
    history: List[AgentMessageView]
    artifacts: Dict[str, Any]
    last_result: Optional[AgentResultView]

    @classmethod
    def from_state(cls, state: WorkflowState) -> "WorkflowStateView":
        history_views = [AgentMessageView.from_model(msg) for msg in state.get("history", [])]
        last_result = AgentResultView.from_payload(state.get("last_result"))
        return cls(
            workflow_id=state["workflow_id"],
            current_phase=state.get("phase"),
            pending_confirmation=state.get("pending_confirmation", False),
            history=history_views,
            artifacts=state.get("artifacts", {}),
            last_result=last_result,
        )
