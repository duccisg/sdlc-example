from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.integrations.langfuse_client import LangfuseProvider
from app.schemas import (
    ContinueWorkflowRequest,
    StartWorkflowRequest,
    WorkflowStateView,
)
from app.services.agent_manager import AgentRegistry
from app.services.workflow_orchestrator import (
    InvalidWorkflowTransition,
    WorkflowNotFoundError,
    WorkflowOrchestrator,
)
from app.utils.llm import create_default_llm
from app.workflows.sdlc_graph import SDLCWorkflowGraph, WorkflowConfig


settings = get_settings()
llm = create_default_llm(settings)
registry = AgentRegistry(llm)
langfuse_provider = LangfuseProvider(settings)
workflow_graph = SDLCWorkflowGraph(WorkflowConfig(registry=registry, langfuse=langfuse_provider))
orchestrator = WorkflowOrchestrator(workflow_graph)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/workflows", response_model=WorkflowStateView)
def start_workflow(payload: StartWorkflowRequest):
    state = orchestrator.start(payload.prompt)
    return WorkflowStateView.from_state(state)


@app.post("/api/workflows/{workflow_id}/confirm", response_model=WorkflowStateView)
def confirm_workflow_step(workflow_id: str, payload: ContinueWorkflowRequest):
    try:
        state = orchestrator.continue_with_confirmation(workflow_id, payload.message)
        return WorkflowStateView.from_state(state)
    except WorkflowNotFoundError as exc:  # pragma: no cover - runtime guard
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidWorkflowTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/workflows/{workflow_id}", response_model=WorkflowStateView)
def get_workflow_state(workflow_id: str):
    try:
        state = orchestrator.get_state(workflow_id)
        return WorkflowStateView.from_state(state)
    except WorkflowNotFoundError as exc:  # pragma: no cover - runtime guard
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.patch("/api/workflows/{workflow_id}", response_model=WorkflowStateView)
def update_workflow_message(workflow_id: str, payload: ContinueWorkflowRequest):
    try:
        state = orchestrator.update_user_message(workflow_id, payload.message or "")
        return WorkflowStateView.from_state(state)
    except WorkflowNotFoundError as exc:  # pragma: no cover - runtime guard
        raise HTTPException(status_code=404, detail=str(exc)) from exc
