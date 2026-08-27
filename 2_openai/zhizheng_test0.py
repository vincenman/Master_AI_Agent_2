import os
from openai import OpenAI
import openai
import requests
import time
import json
import time


from dotenv import load_dotenv
import os
load_dotenv(override=True)


# Pass base_url to the OpenAI client instance
client = OpenAI(
    api_key=os.getenv("ZHIZHENG_API_KEY"),
    base_url="https://api.zhizengzeng.com/v1/"
)

# chat
def chat_completions3(query):    
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]
    )
    print(resp)
    print(resp.choices[0].message.content)

chat_completions3("请帮我写一首关于春天的诗。")