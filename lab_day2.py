# chat completions API
"""
1. Simplest way to call an LLM
2. It is called chat completion as it tells LLM: here is a conversation, please predict what should come next
3. It was created by OpenAI, however, now everyone uses it due to its popularity. Now, all other companies and open source libraries use this, therefore leading to same syntex across.
"""

# import os that we can interact with the OS and then import env file
import os

from dotenv import load_dotenv



load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

# check if API key is present and format is as per key provider.
if not api_key:
    print("No API key was found. Please check .env file.")
elif not api_key.startswith(
    "sk-proj-"
):  # format for openai key, for other providers, check the format and set this up accordingly.
    print(
        "An API key was found, but it does not follow the provider format. Please check API key for correctness."
    )
else:
    print("API key found, format correct.")
print(os.environ)