import os
from dotenv import load_dotenv
from pypdf import PdfReader
from openai import OpenAI
from IPython.display import Markdown, display
import json
import gradio as gr

load_dotenv(override=True)
openai = OpenAI()

reader = PdfReader("twin/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

print(linkedin)

with open("twin/summary.txt", "r", encoding="utf-8") as f:  
    summary = f.read()
    print(summary)


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
Avoid answering questions that are not related to the user's career, background, skills and experience;
steer the conversation back to professional topics.

Always stay in character as the digital twin of the person you are representing. Represent the person.

IMPORTANT: If you don't know the answer, say so. Never make up an answer.
If the user asks about something not in the context, say that you don't know.
"""

print(system_prompt)





def chat(messages,history):
    # history = [{"role": h["role"], "content": h["content"]} for h in history]
    messages = [
        {
            "role": "system",
            "content": system_prompt
        } ] + history + [
        {
            "role": "user",
            "content": messages
        }
    ]
    response = openai.chat.completions.create(model = "gpt-5.4-mini", messages=messages)
    return response.choices[0].message.content



# gr.ChatInterface(chat).launch(inbrowser=True)

# NOW TOOLS

def record_email_tool(email):
     print(f"Tool called to record an email: {email}")
     with open("email.txt", "a", encoding="utf-8") as f:
         f.write(email + "\n")
     return "Email received"
record_email_tool("test2@example.com")



record_email_tool_json = {
    "name": "record_email_tool",
    "description": "Record that the user provided their email address.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address provided by the user."
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }

}   

tools = [{"type": "function", "function": record_email_tool_json}]

print(tools)



def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages, tools=tools)
         
    while response.choices[0].finish_reason=="tool_calls":
            message = response.choices[0].message
            messages.append(message)
            for tool_call in message.tool_calls:
                email = json.loads(tool_call.function.arguments).get("email")
                record_email_tool(email)
                messages.append({"role": "tool", "content": "Email recorded", "tool_call_id": tool_call.id})
            response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages, tools=tools)
            
    return response.choices[0].message.content


gr.ChatInterface(chat).launch(inbrowser=True)

# # Evaluating the chat interface with the email recording tool

# evaluator_chat = """
#  I want to evaluate the response whether itfalls only acceptable criteria. 
#  Will provide response, chat  history and current chat context.
#  AI is using linkedin profile: {linkedin} and summary {summary}.
#  """

# messages = [{"role": "user", "content": evaluator_chat}]

# responses = chat("Please evaluate the following chat history.", messages)
# print(responses)