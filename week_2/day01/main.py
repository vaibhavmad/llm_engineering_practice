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
openrouter_base_url = "https://openrouter.ai/api/v1"
ollama_base_url = "http://localhost:11434/v1"

# now setting up instances of each of the providers
open_ai_client = OpenAI()
google_client = OpenAI(api_key=google_api_key, base_url=google_base_url)
openrouter_client = OpenAI(api_key=openrouter_api_key, base_url=openrouter_base_url)
ollama_client = OpenAI(api_key='ollama', base_url=ollama_base_url)


# now we run all the created LLMs one by one and ask them to output a joke
tell_a_joke = [
    {"role": "user", "content": "Tell a joke for a student who has ADHD and is learning LLM Engineering."}
]

response = open_ai_client.chat.completions.create(model='gpt-4.1-mini-2025-04-14', messages=tell_a_joke) # type: ignore
print(response.choices[0].message.content)

"""
response:
Why did the ADHD student bring a fidget spinner to their LLM engineering class?

Because even their attention span wanted to do a *spin* on language models!
"""

response = google_client.chat.completions.create(model='gemini-3.1-flash-lite', messages=tell_a_joke) # type: ignore
print(response.choices[0].message.content)

"""
response:
Here is a joke for the LLM Engineer whose brain has 47 tabs open, 12 of which are playing music they aren't listening to:

***

**Why did the ADHD student struggle to fine-tune their LLM?**

Because every time the training loss started to converge, they realized they could optimize the prompt engineering pipeline, which led them down a rabbit hole of reading white papers on RAG architectures, which made them remember they needed to update their PyTorch dependencies, which reminded them they hadn’t eaten since 10:00 AM, which triggered a sudden realization that they could build a "Task-Manager-GPT" to solve their own life...

...and now they have three unfinished LLM projects, a half-written blog post about vector databases, and a sudden, burning desire to learn how to play the cello.

**The model's current status?** It’s still at 0% training, but it has a *very* impressive system prompt.
"""

response = ollama_client.chat.completions.create(model='gemma3:270m', messages=tell_a_joke) # type: ignore
print(response.choices[0].message.content)

"""
response:
Why did the LLM engineer get fired from his original job? 

Because he kept trying to build LLMs that could predict the future! 
"""