import os
from openai import OpenAI
from swarm import Swarm, Agent
from swarm.types import ModelSettings
from agents import Agent, WebSearchTool, trace, Runner, gen_trace_id, function_tool

# 1. Define custom base URL and API Key
from dotenv import load_dotenv
load_dotenv(override=True)


API_SECRET_KEY = os.getenv("ZHIZHENG_API_KEY")
BASE_URL = "https://api.zhizengzeng.com/v1/"

# 2. Instantiate a custom OpenAI client with your base_url
custom_openai_client = OpenAI(
    api_key=API_SECRET_KEY,
    base_url=BASE_URL
)

# 3. Pass your custom client into the Swarm runner
client = Swarm(client=custom_openai_client)

INSTRUCTIONS = "You are a web search research agent. Search for current information when requested."

# 4. Define your Agent normally
search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)

# 5. Run the Swarm Agent
response = client.run(
    agent=search_agent,
    messages=[{"role": "user", "content": "What is the latest news today?"}],
)

print(response.messages[-1]["content"])