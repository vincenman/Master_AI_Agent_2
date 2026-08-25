# %% [markdown]
# ## Week 2 Day 2
# 
# Our first Agentic Framework project!!
# 
# Prepare yourself for something ridiculously easy.
# 
# We're going to build a simple Agent system for generating cold sales outreach emails:
# 1. Agent workflow
# 2. Use of tools to call functions
# 3. Agent collaboration via Tools and Handoffs

# %% [markdown]
# <table style="margin: 0; text-align: left; width:100%">
#     <tr>
#         <td style="width: 150px; height: 150px; vertical-align: middle;">
#             <img src="../assets/stop.png" width="150" height="150" style="display: block;" />
#         </td>
#         <td>
#             <h2 style="color:#ff7800;">IMPORTANT PLEASE READ - Emails with SendGrid</h2>
#             <span style="color:#ff7800;">We are going to use the email provider SendGrid. But this is OPTIONAL.<br/>
#             The next cell contains instructions for SendGrid. But if this gives you problems, or if you'd rather use any alternative,<br/>
#             please see <a href="https://edwarddonner.com/faq">Q29 on the FAQ page here</a> for the full explanation and alternatives.
#             </span>
#         </td>
#     </tr>
# </table>

# %% [markdown]
# ## Setting up SendGrid
# 
# 
# Please visit Sendgrid at: https://sendgrid.com/
# 
# (Sendgrid is a Twilio company for sending emails.)
# 
# __If SendGrid gives you problems, see the alternative implementations on Q29 of my FAQ page at https://edwarddonner.com/faq that includes "Resend Email" in community_contributions/2_lab2_with_resend_email and just skipping email altogether.__
# 
# Setting up a SendGrid account is free! (at least, for me, right now).
# 
# Once you've created an account, click on:
# 
# Settings (left sidebar) >> API Keys >> Create API Key (button on top right)
# 
# Copy the key to the clipboard, then add a new line to your .env file:
# 
# `SENDGRID_API_KEY=xxxx`
# 
# And also, within SendGrid, go to:
# 
# Settings (left sidebar) >> Sender Authentication >> "Verify a Single Sender"  
# and verify that your own email address is a real email address, so that SendGrid can send emails for you.

# %%
import os
import asyncio
from typing import Dict
from dotenv import load_dotenv
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, trace, function_tool, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

# %%
load_dotenv(override=True)

# %%
# Let's just check emails are working for you

def send_test_email():
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("vincentman1027@gmail.com")  # Change to your verified sender
    to_email = To("lambenny947@gmail.com")  # Change to your recipient
    content = Content("text/plain", "This is an important test email")
    mail = Mail(from_email, to_email, "Test email", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(response.status_code)

send_test_email()

# %% [markdown]
# ### Did you receive the test email
# 
# If you get a 202, then you're good to go!

# %% [markdown]
# ## Step 1: Agent workflow

# %%
instructions1 = "You are a sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write professional, serious cold emails."

instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write witty, engaging cold emails that are likely to get a response."

instructions3 = "You are a busy sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write concise, to the point cold emails."

# %%
model_DEEPSEEK_CHAT = "deepseek/deepseek-chat"

# %%
# 1. Initialize AsyncOpenAI client configured for OpenRouter
openrouter_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# 2. Wrap the client in OpenAIChatCompletionsModel with your target model
model = OpenAIChatCompletionsModel(
    model=model_DEEPSEEK_CHAT,
    openai_client=openrouter_client
)

# %%
sales_agent1 = Agent(
        name="Professional Sales Agent",
        instructions=instructions1,
        model=model
)

sales_agent2 = Agent(
        name="Engaging Sales Agent",
        instructions=instructions2,
        model=model
)

sales_agent3 = Agent(
        name="Busy Sales Agent",
        instructions=instructions3,
        model=model
)

# %%
# Fix 1: Wrap top-level stream iteration in async function
async def run_streaming_demo():
    result = Runner.run_streamed(sales_agent1, input="Write a cold sales email")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

asyncio.run(run_streaming_demo())

# %%
set_tracing_disabled(True)

# Fix 2: Wrap parallel gather in async function
async def run_parallel_emails():
    message = "Write a cold sales email"
    with trace("Parallel cold emails"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )

    outputs = [result.final_output for result in results]
    for output in outputs:
        print(output + "\n\n")

asyncio.run(run_parallel_emails())

# %%
sales_picker = Agent(
    name="sales_picker",
    instructions="You pick the best cold sales email from the given options. \
Imagine you are a customer and pick the one you are most likely to respond to. \
Do not give an explanation; reply with the selected email only.",
    model=model
)

# %%
# Fix 3: Wrap picker selection in async function
async def run_sales_picker():
    message = "Write a cold sales email"
    print('model_DEEPSEEK_CHAT:' + model_DEEPSEEK_CHAT)

    with trace("Selection from sales people"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )
        outputs = [result.final_output for result in results]

        emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(outputs)

        best = await Runner.run(sales_picker, emails)

        print(f"Best sales email:\n{best.final_output}")

asyncio.run(run_sales_picker())

# %% [markdown]
# ## Part 2: use of tools

# %%
sales_agent1 = Agent(
        name="Professional Sales Agent",
        instructions=instructions1,
        model="gpt-4o-mini",
)

sales_agent2 = Agent(
        name="Engaging Sales Agent",
        instructions=instructions2,
        model="gpt-4o-mini",
)

sales_agent3 = Agent(
        name="Busy Sales Agent",
        instructions=instructions3,
        model="gpt-4o-mini",
)

# %%
@function_tool
def send_email(body: str):
    """ Send out an email with the given body to all sales prospects """
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("vincentman1027@gmail.com")  # Change to your verified sender
    to_email = To("lambenny947@gmail.com")  # Change to your recipient
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, "Sales email", content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}

# %%
description = "Write a cold sales email"

tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)

tools = [tool1, tool2, tool3, send_email]

# %%
manager_instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
 
Follow these steps carefully:
1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
 
3. Use the send_email tool to send the best email (and only the best email) to the user.
 
Crucial Rules:
- You must use the sales agent tools to generate the drafts — do not write them yourself.
- You must send ONE email using the send_email tool — never more than one.
"""

sales_manager = Agent(name="Sales Manager", instructions=manager_instructions, tools=tools, model="gpt-4o-mini")

# Fix 4: Wrap sales manager run in async function
async def run_sales_manager():
    message = "Send a cold sales email addressed to 'Dear CEO'"
    with trace("Sales manager"):
        result = await Runner.run(sales_manager, message)
        print(result)

asyncio.run(run_sales_manager())

# %% [markdown]
# ### Handoffs representation

# %%
subject_instructions = "You can write a subject for a cold sales email. \
You are given a message and you need to write a subject for an email that is likely to get a response."

html_instructions = "You can convert a text email body to an HTML email body. \
You are given a text email body which might have some markdown \
and you need to convert it to an HTML email body with simple, clear, compelling layout and design."

subject_writer = Agent(name="Email subject writer", instructions=subject_instructions, model="gpt-4o-mini")
subject_tool = subject_writer.as_tool(tool_name="subject_writer", tool_description="Write a subject for a cold sales email")

html_converter = Agent(name="HTML email body converter", instructions=html_instructions, model="gpt-4o-mini")
html_tool = html_converter.as_tool(tool_name="html_converter", tool_description="Convert a text email body to an HTML email body")

# %%
@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """ Send out an email with the given subject and HTML body to all sales prospects """
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("vincentman1027@gmail.com")  # Change to your verified sender
    to_email = To("lambenny947@gmail.com")  # Change to your recipient
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}

# %%
tools = [subject_tool, html_tool, send_html_email]

emailer_agent = Agent(
    name="Email Manager",
    instructions="You are an email formatter and sender. You receive the body of an email to be sent. \
You first use the subject_writer tool to write a subject for the email, then use the html_converter tool to convert the body to HTML. \
Finally, you use the send_html_email tool to send the email with the subject and HTML body.",
    tools=tools,
    model="gpt-4o-mini",
    handoff_description="Convert an email to HTML and send it")

# %%
tools = [tool1, tool2, tool3]
handoffs = [emailer_agent]

sales_manager_instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
 
Follow these steps carefully:
1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
You can use the tools multiple times if you're not satisfied with the results from the first try.
 
3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email Manager' agent. The Email Manager will take care of formatting and sending.
 
Crucial Rules:
- You must use the sales agent tools to generate the drafts — do not write them yourself.
- You must hand off exactly ONE email to the Email Manager — never more than one.
"""

sales_manager_handoff = Agent(
    name="Sales Manager",
    instructions=sales_manager_instructions,
    tools=tools,
    handoffs=handoffs,
    model="gpt-4o-mini")

# Fix 5: Wrap automated SDR handoff execution in async function
async def run_automated_sdr():
    message = "Send out a cold sales email addressed to Dear CEO from Alice"
    with trace("Automated SDR"):
        result = await Runner.run(sales_manager_handoff, message)
        print(result)

asyncio.run(run_automated_sdr())