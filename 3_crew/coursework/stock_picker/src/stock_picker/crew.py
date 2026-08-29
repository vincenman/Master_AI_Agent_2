import os
from pathlib import Path

from dotenv import load_dotenv
from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import List

from .tools.push_tool import PushNotificationTool

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


def _proxy_embedder() -> dict:
    """Embedder routed through the zhizengzeng proxy for the memory system."""
    return {
        "provider": "openai",
        "config": {
            "model_name": "text-embedding-3-small",
            "api_base": os.getenv("OPENAI_BASE_URL", "https://api.zhizengzeng.com/v1/"),
            "api_key": os.getenv("ZHIZHENG_API_KEY") or os.getenv("OPENAI_API_KEY"),
        },
    }


class TrendingCompany(BaseModel):
    """ A company that is in the news and attracting attention """
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    reason: str = Field(description="Reason this company is trending in the news")

class TrendingCompanyList(BaseModel):
    """ List of multiple trending companies that are in the news """
    companies: List[TrendingCompany] = Field(description="List of companies trending in the news")

class TrendingCompanyResearch(BaseModel):
    """ Detailed research on a company """
    name: str = Field(description="Company name")
    market_position: str = Field(description="Current market position and competitive analysis")
    future_outlook: str = Field(description="Future outlook and growth prospects")
    investment_potential: str = Field(description="Investment potential and suitability for investment")

class TrendingCompanyResearchList(BaseModel):
    """ A list of detailed research on all the companies """
    research_list: List[TrendingCompanyResearch] = Field(description="Comprehensive research on all trending companies")


@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(config=self.agents_config['trending_company_finder'],
                     llm=_proxy_llm(),
                     tools=[SerperDevTool()], memory=True)
    
    @agent
    def financial_researcher(self) -> Agent:
        return Agent(config=self.agents_config['financial_researcher'], 
                     llm=_proxy_llm(),
                     tools=[SerperDevTool()])

    @agent
    def stock_picker(self) -> Agent:
        return Agent(config=self.agents_config['stock_picker'], 
                     llm=_proxy_llm(),
                     tools=[PushNotificationTool()], memory=True)
    
    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'],
            output_pydantic=TrendingCompanyList,
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'],
            output_pydantic=TrendingCompanyResearchList,
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'],
        )
    




    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""

        manager = Agent(
            config=self.agents_config['manager'],
            llm=_proxy_llm(),
            allow_delegation=True
        )
            
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
            memory=True,
            embedder=_proxy_embedder(),
        )
