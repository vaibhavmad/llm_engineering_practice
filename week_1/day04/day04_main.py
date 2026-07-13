# Today we cover:
# 1. Understanding Transformers: The Architecture Behind GPT and LLMs
# 2. From LSTMs to Transformers: Attention, Emergent Intelligence & Agentic A
# 3. Parameters: From Millions to Trillions in GPT, LLaMA & DeepSeek
# 4. What Are Tokens? From Characters to GPT's Tokenizer
# 5. Understanding Tokenization: How GPT Breaks Down Text into Tokens
# 6. Tokenizing with tiktoken and Understanding the Illusion of Memory
# 7. Context Windows, API Costs, and Token Limits in LLMs

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
print(tokens)
# now using a for loop, we are decoding each token number and printing it next to each token 
token_count = 0
for token_id in tokens:
    token_text = encoding.decode([token_id])
    print(f"{token_id} = {token_text}")
    token_count += 1
print(f"total tokens: {token_count}")

# Output here is:
# 12194 = Hi
# 11 = ,
# 922 =  my
# 8340 =  favorite
# 2086 =  number
# 382 =  is
# 220 =  
# 16 = 1
# 13 = .
# 35862 = 618
# 16620 = 145
# 20469 = 167
# 7479 = 89


# Next, we do a simple experiment to understand that individual LLMs do not have any memory. Every prompt sent over to the LLM is fresh, until and unless we do not share the history of the conversation.


ai_llm = openai.OpenAI()
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hi, my favorite number is 1.61814516789"}
]

response = ai_llm.chat.completions.create(model='gpt-4.1-nano-2025-04-14', messages=messages)
print(response.choices[0].message.content)


# Now response received is:
# Hello! That's a fascinating favorite number—quite close to the golden ratio (approximately 1.6180339). Are you interested in mathematics, aesthetics, or something else related to this number?


# as we can see, we have just possed on some info to the LLM, however, if we ask it a follow up question connected to the last prompt, lets see what we get? Most probably it will tell us that it is not privy to our personal info.

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is my favorite number?"}
]

response = ai_llm.chat.completions.create(model='gpt-4.1-nano-2025-04-14', messages=messages)
print(response.choices[0].message.content)
# now the response is:
# I don't have access to personal information unless you share it with me. Could you tell me what your favorite number is?

# However, if we want to kind of continue chatting with the LLM, we need to add another role, which is assistant and pass on this information also with the other info that we are sending, here's a quick example:

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hi, my favorite number is 1.61814516789"},
    {"role": "assistant", "content": "Hello! That's a fascinating favorite number—quite close to the golden ratio (approximately 1.6180339). Are you interested in mathematics, aesthetics, or something else related to this number?"},
    {"role": "user", "content": "What is my favorite number?"}
]

response = ai_llm.chat.completions.create(model='gpt-4.1-nano-2025-04-14', messages=messages)
print(response.choices[0].message.content)


# now on the basis of supplied info, it was able to continue answering. response was: Your favorite number is 1.61814516789.
# hence
# 1. every call to an LLM is completely stateless
# 2. we pass in the entire conversation so far in the input prompt every time
# 3. this gives the illusion that LLM has memory
# 4. however, this is a trick or the conversation that we see in the chat interfaces these days is basically the by product of passing on this information to an LLM in every prompt
# 5. LLM just responds by predicting the most likely next token in the sequence, and it feels like we are talking to an intelligent being

# this information that is passed to an LLM in a conversation is called context. Every LLM has a limit to the amount of tokens it can intake in one go, and is known as context window.

# plus, in addition to the context that we send across, LLM starts working on the response in the background. In this process, every new token generated by the LLM, for example in case of the last response, lets consider each word is a token, then each of the token is passed back, such as the original context that we gave as input + Your, then it outputs Your favorite, which again gets added to the content window such as input + Your favorite and so on.

# the context window limits govern how much a model can remember and refer to in the ongoing conversation
