from openai import OpenAI
from swarm import Swarm, Agent


from dotenv import load_dotenv
import os
load_dotenv(override=True)


# Pass base_url to the OpenAI client instance
custom_client = OpenAI(
    api_key=os.getenv("ZHIZHENG_API_KEY"),
    base_url="https://api.zhizengzeng.com/v1/"
)

# Pass that client to Swarm
client = Swarm(client=custom_client)

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)

# Run using the custom swarm client
response = client.run(agent=search_agent, messages=[...])