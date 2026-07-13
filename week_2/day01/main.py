# covered today:
# using multiple LLM API providers, such as openAI, anthropic, deepseek, google, groq, and also we shall be using openrouter
# additionaly, shall we using briefly though, langchain and liteLLM

# step 1: we import the API keys from env file
import os
from dotenv import load_dotenv

load_dotenv(override=True)

open_ai_api_key = os.getenv('OPENAI_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')
openrouter_api_key = os.getenv('OPENROUTER_API_KEY')

# to ensure that the keys are loaded and are as per the format, we write the below code, if a key is not loaded properly, system gives us an error

if not open_ai_api_key:
    print("OpenAI API Key not found")
elif not open_ai_api_key.startswith("sk-proj-"):
    print("Check OPEN AI API Key's format.")

if not google_api_key:
    print("Google API Key not found")
elif not google_api_key.startswith("AQ."):
    print("Check Google API Key's format.")

if not openrouter_api_key:
    print("Open Router API Key not found")
elif not openrouter_api_key.startswith("sk-or-v1-"):
    print("Check Open Router API Key's format.")
