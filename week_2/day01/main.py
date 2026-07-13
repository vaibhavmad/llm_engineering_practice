# covered today:
# using multiple LLM API providers, such as openAI, anthropic, deepseek, google, groq, and also we shall be using openrouter
# additionaly, shall we using briefly though, langchain and liteLLM

# step 1: we import the API keys from env file
import os
from dotenv import load_dotenv
from openai import OpenAI


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


# adding URL's for each non open ai provider, so as to use open ai lib to run these llms
google_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
openrouter_base_url = "https://openrouter.ai/api/v1/chat/completions"
ollama_base_url = "http://localhost:11434"

# now setting up instances of each of the providers
open_ai_client = OpenAI()
google_client = OpenAI(api_key=google_api_key, base_url=google_base_url)
openrouter_client = OpenAI(api_key=openrouter_api_key, base_url=openrouter_base_url)
ollama_client = OpenAI(api_key='ollama', base_url=ollama_base_url)

