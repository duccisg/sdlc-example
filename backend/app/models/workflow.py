from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field


class SDLCPhase(str, Enum):
    INTAKE = "intake"
    ANALYSIS = "analysis"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    RETROSPECTIVE = "retrospective"


class AgentMessage(BaseModel):
    sender: str = Field(description="Name of the entity that produced the message")
    phase: SDLCPhase = Field(description="Phase associated with the message")
    content: str = Field(description="Natural language content for the message")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    agent: str = Field(description="Agent identifier")
    phase: SDLCPhase = Field(description="Phase that produced the result")
    output: str = Field(description="Primary textual response")
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    requires_confirmation: bool = Field(default=True)
    suggested_next_phase: Optional[SDLCPhase] = Field(default=None)


class WorkflowState(TypedDict, total=False):
    phase: SDLCPhase
    history: List[AgentMessage]
    artifacts: Dict[str, Any]
    pending_confirmation: bool
    last_result: Optional[Dict[str, Any]]
    workflow_id: str
    user_message: Optional[str]


class WorkflowEvent(BaseModel):
    workflow_id: str
    phase: SDLCPhase
    message: AgentMessage
