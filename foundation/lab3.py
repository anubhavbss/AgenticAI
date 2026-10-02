## The first big project - The Digital Twin

### But first: introducing Pushover

# Pushover is a notification tool for sending Push Notifications to your phone.

# It's super easy to set up and install!

# Simply visit https://pushover.net/ and click 'Login or Signup' on the top right to sign up for a free account, and create your API keys.

# Once you've signed up, on the home screen, click "Create an Application/API Token", and give it any name (like Agents) and click Create Application.

# Then add 2 lines to your `.env` file:

# PUSHOVER_USER=_put the key that's on the top right of your Pushover home screen and probably starts with a u_  
# PUSHOVER_TOKEN=_put the key when you click into your new application called Agents (or whatever) and probably starts with an a_

# Remember to save your `.env` file, and run `load_dotenv(override=True)` after saving, to set your environment variables.

# Finally, click "Add Phone, Tablet or Desktop" to install on your phone.

import os
from dotenv import load_dotenv
import gradio as gr
import requests
import json
from pypdf import PdfReader
from openai import OpenAI
# usual start
load_dotenv(override=True)
openai = OpenAI()
from agents import Agent, trace, Runner

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")    
pushover_url = "https://api.pushover.net/1/messages.json"
if pushover_user:
    if pushover_user.startswith("u"):
        print("Pushover user key looks valid.")
    else:
        print("Pushover user key does not look valid and doesnot start with 'u'.")

if pushover_token:
    if pushover_token.startswith("a"):
        print("Pushover token looks valid.")
    else:
        print("Pushover token does not look valid and does not start with 'a'.")


def push(message):
    print(f"Pushing message: {message}")
    payload ={"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url,data=payload)    

push("Hello, this is a test message!")

# Tools for recording user details and unknown questions.

def record_user_details(email, name="Name not provided", note="No notes provided"):
    push(f"Recorded interest from {name} with email {email} and note {note}")
    return "OK"

def record_unknown_question(question):
    push(f"Recording {question} and asked that I could not answer")
    return "OK"

# JSON schema for the record_user_details tool.
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
        
          "email": {"type": "string", "description": "This is email of user"},
          "name": {"type": "string", "description": "This is the name of the user, if provided by user"},
          "note": {"type": "string", "description": "Interested in the project"}
        }
    },
    "required": ["email"],
    "additionalProperties": False

}

# JSON schema for the record_unknown_question tool.
record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
          "question": {"type": "string", "description": "The question that could not be answered"}
        },
    
    "required": ["question"],
    "additionalProperties": False
}
}
# List of tools available for the digital twin to use.
tools = [{"type": "function", "function": record_user_details_json}, {"type": "function", "function": record_unknown_question_json}]
    

type(tools)

def handle_tool_calls(tool_calls):
    # The structure of this function is dictated by the OpenAI tool-calling protocol:
    # 1. The model may return MANY tool calls at once -> so we loop and collect `results`.
    # 2. Each tool_call carries `function.name` (which Python function to run) and
    #    `function.arguments` (a JSON *string*) -> so we json.loads it into a dict.
    # 3. We map the name -> the real function. globals().get(name) works because our
    #    JSON schema "name" fields match the Python function names exactly
    #    (record_user_details / record_unknown_question). A dict like
    #    {"record_user_details": record_user_details, ...} would be a safer alternative.
    # 4. We call it with **arguments so the JSON keys become keyword arguments.
    # 5. We must send one message back per tool call with role="tool" and the SAME
    #    tool_call_id, so the model can match each result to the call it made.
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else "No tool found"
        results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
    return results

reader = PdfReader("twin/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text
print(linkedin)        
        
with open("twin/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()


system_prompt = f"""

# Your role

You are a digital twin running on a website, chatting with visitors of the website.
You represent the person who's website you are on.
You answer questions related to their career, background, skills and experience.

Here are the details of the person you are representing:

{summary}

If asked, you explain clearly that you are an AI that is the digital twin of this person.

# Context

Here is a summary of the person's LinkedIn profile so that you can answer questions:

{linkedin}

# Rules

Engage with the user. Be professional and engaging, as if talking to a potential client or future employer who came across the website.
Only answer questions related to career, background, skills and experience.
If the user asks about something unrelated, then steer the conversation back to professional topics.

Always stay in character as the digital twin of the person you are representing. Represent the person.

If the user would like to get in touch, then ask for their email, and use your tool to record their email for follow-up.

IMPORTANT:
If you don't know the answer, use your tool to record the question, and then tell the user that you don't know. Never make up an answer.
"""

# Chat function for interacting with the digital twin.
def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages, tools=tools)
    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_calls = message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages, tools=tools)
    return response.choices[0].message.content

gr.ChatInterface(chat).launch(inbrowser=True)

# Create Guradrail for the chat

# gaudrail_agent = Agent("user": system_prompt, instructions=""" )