import os
from openai import OpenAI
import openai
import requests
import time
import json
import time


# The imports

from dotenv import load_dotenv
load_dotenv(override=True)


API_SECRET_KEY = os.getenv("ZHIZHENG_API_KEY")
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
    #print(resp.choices[0].message.content)

chat_completions3("请帮我写一篇关于人工智能的文章，要求不少于500字。")