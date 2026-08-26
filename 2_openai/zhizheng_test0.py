import os
from openai import OpenAI
import openai
import requests
import time
import json
import time

API_SECRET_KEY = "sk-zk289953c1e2db3a772a733ecfce902cf6c6a8ea15100233";
BASE_URL = "https://api.zhizengzeng.com/v1/"

# chat
def chat_completions3(query):
    client = OpenAI(api_key=API_SECRET_KEY, base_url=BASE_URL)
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