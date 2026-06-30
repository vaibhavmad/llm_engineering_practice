"""
Today we cover:
1. Understanding Transformers: The Architecture Behind GPT and LLMs
2. From LSTMs to Transformers: Attention, Emergent Intelligence & Agentic A
3. Parameters: From Millions to Trillions in GPT, LLaMA & DeepSeek
4. What Are Tokens? From Characters to GPT's Tokenizer
5. Understanding Tokenization: How GPT Breaks Down Text into Tokens
6. Tokenizing with tiktoken and Understanding the Illusion of Memory
7. Context Windows, API Costs, and Token Limits in LLMs
"""
# using tiktoken to encode and decode given prompt into token numbers on the basis of a given LLM model name
# import the library we are using for this exercise.
import tiktoken
import openai
import os
from dotenv import load_dotenv
load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("No API key was found. Please check .env file.")
elif not api_key.startswith("sk-proj-"):  # format for openai key, for other providers, check the format and set this up accordingly.
    print("An API key was found, but it does not follow the provider format. Please check API key for correctness.")

# create a variable, that will have the name of the model passed into it
encoding = tiktoken.encoding_for_model('gpt-5')
# on the basis of given model name, we are encoding a given text into token numbers 
tokens = encoding.encode("Hi, my favorite number is 1.61814516789")
# here we can print all the token numbers in one go, which is output as a list.
# print(tokens)
# now using a for loop, we are decoding each token number and printing it next to each token 
token_count = 0
for token_id in tokens:
    token_text = encoding.decode([token_id])
    print(f"{token_id} = {token_text}")
    token_count += 1
print(f"total tokens: {token_count}")
"""
Output here is:
12194 = Hi
11 = ,
922 =  my
8340 =  favorite
2086 =  number
382 =  is
220 =  
16 = 1
13 = .
35862 = 618
16620 = 145
20469 = 167
7479 = 89
"""
