from __future__ import annotations

from typing import Dict

from app.agents.analysis_agent import SolutionAnalysisAgent
from app.agents.base import SDLCBaseAgent
from app.agents.deployment_agent import DeploymentAgent
from app.agents.design_agent import SolutionDesignAgent
from app.agents.implementation_agent import ImplementationAgent
from app.agents.intake_agent import RequirementIntakeAgent
from app.agents.retrospective_agent import RetrospectiveAgent
from app.agents.testing_agent import TestingAgent
from app.models.workflow import SDLCPhase
from app.utils.llm import BaseChatModel


class AgentRegistry:
    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm
        self._agents: Dict[SDLCPhase, SDLCBaseAgent] = {}
        self._register_default_agents()

    def _register_default_agents(self) -> None:
        self._agents = {
            SDLCPhase.INTAKE: RequirementIntakeAgent(self._llm),
            SDLCPhase.ANALYSIS: SolutionAnalysisAgent(self._llm),
            SDLCPhase.DESIGN: SolutionDesignAgent(self._llm),
            SDLCPhase.IMPLEMENTATION: ImplementationAgent(self._llm),
            SDLCPhase.TESTING: TestingAgent(self._llm),
            SDLCPhase.DEPLOYMENT: DeploymentAgent(self._llm),
            SDLCPhase.RETROSPECTIVE: RetrospectiveAgent(self._llm),
        }

    def get_agent(self, phase: SDLCPhase) -> SDLCBaseAgent:
        return self._agents[phase]

    def override_agent(self, phase: SDLCPhase, agent: SDLCBaseAgent) -> None:
        self._agents[phase] = agent

    def available_phases(self) -> list[SDLCPhase]:
        return list(self._agents.keys())
