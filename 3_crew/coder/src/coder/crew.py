import os
from pathlib import Path

from dotenv import load_dotenv
from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

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
class Coder():
    """Coder crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # One click install for Docker Desktop:
    #https://docs.docker.com/desktop/

    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config['coder'], # type: ignore[index]
            llm=_proxy_llm(),
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",  # Uses Docker for safety
            max_execution_time=30, 
            max_retry_limit=3 
    )


    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config['coding_task'], # type: ignore[index]
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Coder crew"""


        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
