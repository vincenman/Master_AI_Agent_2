from pydantic import BaseModel, Field
from agents import Agent

HOW_MANY_SEARCHES = 5

INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."


class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")

from dotenv import load_dotenv
import os
load_dotenv(override=True)

from openai import AsyncOpenAI
from agents import set_default_openai_client, set_tracing_disabled


# Pass base_url to the OpenAI client instance
custom_client = AsyncOpenAI(
    api_key=os.getenv("ZHIZHENG_API_KEY"),
    base_url="https://api.zhizengzeng.com/v1/"
)

set_default_openai_client(custom_client, use_for_tracing=False)
# Tracing uploads to platform.openai.com, which is not reachable from HK.
set_tracing_disabled(True)
    
planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)