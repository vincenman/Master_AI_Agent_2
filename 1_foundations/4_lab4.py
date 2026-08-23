# %% [markdown]
# ## The first big project - Professionally You!
# 
# ### And, Tool use.
# 
# ### But first: introducing Pushover
# 
# Pushover is a nifty tool for sending Push Notifications to your phone.
# 
# It's super easy to set up and install!
# 
# Simply visit https://pushover.net/ and click 'Login or Signup' on the top right to sign up for a free account, and create your API keys.
# 
# Once you've signed up, on the home screen, click "Create an Application/API Token", and give it any name (like Agents) and click Create Application.
# 
# Then add 2 lines to your `.env` file:
# 
# PUSHOVER_USER=_put the key that's on the top right of your Pushover home screen and probably starts with a u_  
# PUSHOVER_TOKEN=_put the key when you click into your new application called Agents (or whatever) and probably starts with an a_
# 
# Remember to save your `.env` file, and run `load_dotenv(override=True)` after saving, to set your environment variables.
# 
# Finally, click "Add Phone, Tablet or Desktop" to install on your phone.

# %%
# imports

from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr

# %%
# The usual start

load_dotenv(override=True)

import os
openai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# %%
# For pushover

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

if pushover_user:
    print(f"Pushover user found and starts with {pushover_user[0]}")
else:
    print("Pushover user not found")

if pushover_token:
    print(f"Pushover token found and starts with {pushover_token[0]}")
else:
    print("Pushover token not found")

# %%
def push(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)

# %%
push("HEY!!")

# %%
def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording interest from {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

# %%
def record_unknown_question(question):
    push(f"Recording {question} asked that I couldn't answer")
    return {"recorded": "ok"}

# %%
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

# %%
record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

# %%
tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]

# %%
tools

# %%
# This function can take a list of tool calls, and run them. This is the IF statement!!

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)

        # THE BIG IF STATEMENT!!!

        if tool_name == "record_user_details":
            result = record_user_details(**arguments)
        elif tool_name == "record_unknown_question":
            result = record_unknown_question(**arguments)

        results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
    return results

# %%
globals()["record_unknown_question"]("this is a really hard question")

# %%
# This is a more elegant way that avoids the IF statement.

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}
        results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
    return results

# %%
reader = PdfReader("me/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

with open("me/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

name = "Vincent Man"

# %%
system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
particularly questions related to {name}'s career, background, skills and experience. \
Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."


# %%
# Option A: DeepSeek R1 (Reasoning)
model_DEEPSEEK_R1 = "deepseek/deepseek-r1"

# Option B: DeepSeek V3 (Fast & Powerful General Model)
model_DEEPSEEK_CHAT = "deepseek/deepseek-chat"

# Option C: Qwen 2.5 72B (Excellent Chinese/English Support)
model_QWEN = "qwen/qwen-2.5-72b-instruct"

#Optgion D: Grok 4.6 (Fast & Powerful General Model)    
model_GROK = "x-ai/grok-4.6"



# %%
def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    done = False
    while not done:

        # This is the call to the LLM - see that we pass in the tools json

        response = openai.chat.completions.create(model=model_DEEPSEEK_CHAT, messages=messages, tools=tools)

        finish_reason = response.choices[0].finish_reason
        
        # If the LLM wants to call a tool, we do that!
         
        if finish_reason=="tool_calls":
            message = response.choices[0].message
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    return response.choices[0].message.content

# %%


# %%
gr.ChatInterface(chat, type="messages").launch()

# %% [markdown]
# ## And now for deployment
# 
# This code is in `app.py`
# 
# We will deploy to HuggingFace Spaces.
# 
# Before you start: remember to update the files in the "me" directory - your LinkedIn profile and summary.txt - so that it talks about you! Also change `self.name = "Ed Donner"` in `app.py`..  
# 
# Also check that there's no README file within the 1_foundations directory. If there is one, please delete it. The deploy process creates a new README file in this directory for you.
# 
# And one more thing: this is optional, but you might want to delete the entire folder "community_contributions" within 1_foundations. You can always pull it from github again in the future. But if you don't, then this entire folder gets uploaded to HuggingFace even though we don't need it, and it's become quite large.
# 
# 1. Visit https://huggingface.co and set up an account  
# 2. From the Avatar menu on the top right, choose Access Tokens. Choose "Create New Token". Give it WRITE permissions - it needs to have WRITE permissions! Keep a record of your new key.  
# 3. In the Terminal, run: `uv tool install 'huggingface_hub[cli]'` to install the HuggingFace tool, then `hf auth login --token YOUR_TOKEN_HERE`, like `hf auth login --token hf_xxxxxx`, to login at the command line with your key. Afterwards, run `hf auth whoami` to check you're logged in  
# 4. Take your new token and add it to your .env file: `HF_TOKEN=hf_xxx` for the future
# 5. From the 1_foundations folder, enter: `uv run gradio deploy` 
# 6. Follow its instructions: name it "career_conversation", specify app.py, choose cpu-basic as the hardware, say Yes to needing to supply secrets, provide your openai api key, your pushover user and token, and say "no" to github actions.  
# 
# Thank you Robert, James, Martins, Andras and Priya for these tips.  
# Please read the next 2 sections - how to change your Secrets, and how to redeploy your Space (you may need to delete the README.md that gets created in this 1_foundations directory).
# 
# #### More about these secrets:
# 
# If you're confused by what's going on with these secrets: it just wants you to enter the key name and value for each of your secrets -- so you would enter:  
# `OPENAI_API_KEY`  
# Followed by:  
# `sk-proj-...`  
# 
# And if you don't want to set secrets this way, or something goes wrong with it, it's no problem - you can change your secrets later:  
# 1. Log in to HuggingFace website  
# 2. Go to your profile screen via the Avatar menu on the top right  
# 3. Select the Space you deployed  
# 4. Click on the Settings wheel on the top right  
# 5. You can scroll down to change your secrets (Variables and Secrets section), delete the space, etc.
# 
# #### And now you should be deployed!
# 
# If you want to completely replace everything and start again with your keys, you may need to delete the README.md that got created in this 1_foundations folder.
# 
# Here is mine: https://huggingface.co/spaces/ed-donner/Career_Conversation
# 
# I just got a push notification that a student asked me how they can become President of their country 😂😂
# 
# For more information on deployment:
# 
# https://www.gradio.app/guides/sharing-your-app#hosting-on-hf-spaces
# 
# To delete your Space in the future:  
# 1. Log in to HuggingFace
# 2. From the Avatar menu, select your profile
# 3. Click on the Space itself and select the settings wheel on the top right
# 4. Scroll to the Delete section at the bottom
# 5. ALSO: delete the README file that Gradio may have created inside this 1_foundations folder (otherwise it won't ask you the questions the next time you do a gradio deploy)
# 

# %% [markdown]
# <table style="margin: 0; text-align: left; width:100%">
#     <tr>
#         <td style="width: 150px; height: 150px; vertical-align: middle;">
#             <img src="../assets/exercise.png" width="150" height="150" style="display: block;" />
#         </td>
#         <td>
#             <h2 style="color:#ff7800;">Exercise</h2>
#             <span style="color:#ff7800;">• First and foremost, deploy this for yourself! It's a real, valuable tool - the future resume..<br/>
#             • Next, improve the resources - add better context about yourself. If you know RAG, then add a knowledge base about you.<br/>
#             • Add in more tools! You could have a SQL database with common Q&A that the LLM could read and write from?<br/>
#             • Bring in the Evaluator from the last lab, and add other Agentic patterns.
#             </span>
#         </td>
#     </tr>
# </table>

# %% [markdown]
# <table style="margin: 0; text-align: left; width:100%">
#     <tr>
#         <td style="width: 150px; height: 150px; vertical-align: middle;">
#             <img src="../assets/business.png" width="150" height="150" style="display: block;" />
#         </td>
#         <td>
#             <h2 style="color:#00bfff;">Commercial implications</h2>
#             <span style="color:#00bfff;">Aside from the obvious (your career alter-ego) this has business applications in any situation where you need an AI assistant with domain expertise and an ability to interact with the real world.
#             </span>
#         </td>
#     </tr>
# </table>


