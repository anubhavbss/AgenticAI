import os
from dotenv import load_dotenv
#import json
from openai import OpenAI
# from IPython.display import Markdown, display

load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    print(f"Key exists and start with {openai_api_key [:8]}")
else:
    print(f"Key doesn't exists(it is optional)") 

openai = OpenAI()

question = """"
Create a opentofu github workflow that require PR approval before merging it main branch
also deployment only occure once PR is approved and merge with main branch
"""

question += r" create workflow and save it on my local drive at location C:\Users\anusri\projects\AgenticAI"  

messages = [{"role": "user", "content": question}]

response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages)
answer = response.choices[0].message.content
print(answer)
