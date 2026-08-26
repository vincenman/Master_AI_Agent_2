from openai import OpenAI
from swarm import Swarm, Agent


from dotenv import load_dotenv
import os
import httpx

load_dotenv(override=True)

proxy_key = os.getenv("ZHIZHENG_API_KEY")
if not proxy_key:
    raise SystemExit("ZHIZHENG_API_KEY missing: add it to the repo's .env file")


# Pass base_url to the OpenAI client instance
custom_client = OpenAI(
    api_key=proxy_key,
    base_url="https://api.zhizengzeng.com/v1/"
)

# Pass that client to Swarm
client = Swarm(client=custom_client)


def web_search(query: str) -> str:
    """Search the web via Serper (Google) and return a compact summary of results."""
    response = httpx.post(
        "https://google.serper.dev/search",
        headers={
            "X-API-KEY": os.getenv("SERPER_API_KEY", ""),
            "Content-Type": "application/json",
        },
        json={"q": query, "num": 5},
        timeout=30,
    )
    response.raise_for_status()
    items = response.json().get("organic", [])
    if not items:
        return "No results found."
    return "\n\n".join(
        f"{i + 1}. {item.get('title', '')}\n{item.get('link', '')}\n{item.get('snippet', '')}"
        for i, item in enumerate(items)
    )


INSTRUCTIONS = (
    "You are a research assistant. Given a user question, use web_search to find "
    "relevant information, then answer the question in 2-3 concise paragraphs. "
    "Cite the sources you used."
)

# NOTE: WebSearchTool/ModelSettings are OpenAI Agents SDK classes, not Swarm.
# openai-swarm (PyPI) uses plain functions in `functions=` and tool_choice on
# the Agent itself; "required" would force a tool call on every turn, so the
# agent never finishes answering - left at the default (auto) instead.
search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    functions=[web_search],
    model="gpt-4o-mini",
)

# Run using the custom swarm client
response = client.run(
    agent=search_agent,
    messages=[{"role": "user", "content": "What are the latest advances in AI agents?"}],
    max_turns=5,
)

print("=== transcript ===")
for msg in response.messages:
    role = msg.get("role")
    if msg.get("tool_calls"):
        for call in msg["tool_calls"]:
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            print(f"[{role}] tool call: {name}({args})")
    elif msg.get("tool_call_id"):
        print(f"[{role}] tool result: {msg['content'][:200]}")
    elif msg.get("content"):
        print(f"[{role}] {msg['content']}")

print("\n=== final answer ===")
print(response.messages[-1]["content"])
