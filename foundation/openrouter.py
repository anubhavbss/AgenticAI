
import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI  # Replace with the actual import for LLM  
openai = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="google/gemma-4-26b-a4b-it:free",
)

