import os
from pathlib import Path

from dotenv import load_dotenv
from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from .tools.sandbox_tools import sandbox_tools

# Always use this project's .env (proxy keys), regardless of the launch directory —
# otherwise crewai's dotenv lookup can pick up a parent ~/.env with a different key.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=True)


def _proxy_llm() -> LLM:
    """LLM routed through the zhizengzeng OpenAI-compatible proxy (HK access)."""
    model = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
    if "/" not in model:
        model = f"openai/{model}"
    return LLM(
        model=model,
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.zhizengzeng.com/v1/"),
        api_key=os.getenv("ZHIZHENG_API_KEY") or os.getenv("OPENAI_API_KEY"),
    )


@CrewBase
class EngineeringTeam():
    """EngineeringTeam crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def engineering_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['engineering_lead'],  # type: ignore[index]
            llm=_proxy_llm(),
            verbose=True,
            mcps=["https://mcp.context7.com/mcp"]
        )

    @agent
    def backend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['backend_engineer'],  # type: ignore[index]
            llm=_proxy_llm(),
            verbose=True,
            tools=sandbox_tools
        )

    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['frontend_engineer'],  # type: ignore[index]
            llm=_proxy_llm(),
            verbose=True,
            tools=sandbox_tools,
            mcps=["https://mcp.context7.com/mcp"],
        )

    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_engineer'],  # type: ignore[index]
            llm=_proxy_llm(),
            verbose=True,
            tools=sandbox_tools
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task']  # type: ignore[index]
        )

    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_task'],  # type: ignore[index]
        )

    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['frontend_task'],  # type: ignore[index]
        )

    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_task'],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the EngineeringTeam crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            tracing=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
