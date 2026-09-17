# chat completions API
# 1. Simplest way to call an LLM
# 2. It is called chat completion as it tells LLM: here is a conversation, please predict what should come next
# 3. It was created by OpenAI, however, now everyone uses it due to its popularity. Now, all other companies and open source libraries use this, therefore leading to same syntex across.

# import os that we can interact with the OS and then import env file
import os
import requests
from openai import OpenAI
# import openai API key
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

# check if API key is present and format is as per key provider.
if not api_key:
    print("No API key was found. Please check .env file.")
elif not api_key.startswith("sk-proj-"):  # format for openai key, for other providers, check the format and set this up accordingly.
    print("An API key was found, but it does not follow the provider format. Please check API key for correctness.")
# else:
#     print("API key found, format correct.")

# API key is available and the format is correct
# we convert the else part to a comment, since, this should only run if there's an issue with the API key
# else, if API key is good, then the system shall proceed ahead

# Next we move to endpoints:
# Endpoint is a mix of url address and instructions, that we send to an API provider and get the desired response in return.
# or we send some information and that might change some information in the APIs. We are using HTTP requests, which have two 
# types: GET: Like reading info from API and POST: writing or sending some info to API
# to enable this we use requests library, which has been imported above

# we now start with headers, in this headers, we are first passing on the loaded api key
# then we are telling the api to send information in json format
# headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

# here, in payload, we are telling the api, which model has to be used
# plus, we are setting up the messages format and sending the content to openai api
# payload = {
#     "model": "gpt-5-nano",
#     "messages": [{"role": "user", "content": "Tell me a fun fact."}]
# }

# now we configure our api request
# respose = requests.post(
#     "https://api.openai.com/v1/chat/completions",
#     headers=headers,
#     json=payload
# )

# print(respose.json())

# response received is: 
"""
{'id': 'chatcmpl-Dw07jOxSUetEkuCSxn3AH86y7TpKw', 'object': 'chat.completion', 'created': 1782715871, 'model': 'gpt-5-nano-2025-08-07', 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'Fun fact: Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are still safe to eat after thousands of years. Want another fun fact?', 'refusal': None, 'annotations': []}, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 12, 'completion_tokens': 365, 'total_tokens': 377, 'prompt_tokens_details': {'cached_tokens': 0, 'audio_tokens': 0}, 'completion_tokens_details': {'reasoning_tokens': 320, 'audio_tokens': 0, 'accepted_prediction_tokens': 0, 'rejected_prediction_tokens': 0}}, 'service_tier': 'default', 'system_fingerprint': None}
"""

# in the above response, we have the fun fact, which we can separate by going inside the json
# print(respose.json()['choices'])
# this give us:
"""
[{'index': 0, 'message': {'role': 'assistant', 'content': 'Fun fact: Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are thousands of years old—and still safe to eat—thanks to honey’s low water content and acidic pH, which inhibit bacteria and yeast growth.', 'refusal': None, 'annotations': []}, 'finish_reason': 'stop'}]
"""
# now we are getting a list of dicts, so, ['choices'][0] should give us the list
# then ['choices'][0]['message'] should give us the message only, lets try
# print(respose.json()['choices'][0]['message'])
# now we get:
"""
{'role': 'assistant', 'content': 'Fun fact: Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs over 3,000 years old that are still perfectly edible. Honey’s low water content and acidic pH help keep bacteria away. Want another fun fact?', 'refusal': None, 'annotations': []}
"""
# further extraction:
# print(respose.json()['choices'][0]['message']['content'])
"""
here, we are able to extract the response:
Fun fact: Wombat poop is cube-shaped, which helps it stack up instead of rolling away and marks their territory. Want another fun fact?
"""

"""
Now, this way we used above is perfectly fine, however, here, we are stiching the header requests, we are then navigating through the entire response and get the final result. To get rid of this pain, Open AI created 'openai package', a library created by openai. This helps us by streamlining the requests.
"""

# moving on to openai package
# for this first we add openai lib to our venv, then we import from openai OpenAI, now to use it, we do the following
openai = OpenAI()

# now, to use above, we do the following, this is very similar to what we did above, but instead of defining headers, adding the api endpoint, we simply do openai.chat.completeions.create and then we pass on the model and the messages
# respose = openai.chat.completions.create(model='gpt-5-nano', messages=[{"role": "user", "content": "Tell me a fun fact."}])
# and then instead of going through the reponse and extracting the info, we simple do, lets see what we get
# print(respose.choices[0].message.content)
"""
Fun fact: A single cloud can weigh more than a million pounds. Clouds look fluffy and light, but they're made of enormous amounts of water droplets and ice crystals—that adds up to a surprisingly huge weight. Want another fun fact?
"""

# Now, openai api format is being used by all the other providers also now, which includes athropic, gemini and even ollama. so, we need to remember the following 
"""
chat.completions.create
&
respose.choices[0].message.content)
"""

# therefore if we have to use lets say gemini, we can do gemini = OpenAI() and then setup gemini, though we will have to pass on some more info such as the url and the model name that belongs to gemini. same is the case with ollama, that we shall work on in some time.

"""
we do this like below:
gemini = OpenAI(base_url="we use the endpoint provided here", api_key='provider_api_key')
"""

OLLAMA_BASE_URL = 'http://localhost:11434/v1'
ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key='ollama')

# response = ollama.chat.completions.create(model='llama3.2', messages=[{"role": "user", "content": "Tell me a fun fact."}])
# print(response.choices[0].message.content)

"""
And here's the response from the local LLM:
Here's one:

Did you know that there is a species of jellyfish that is immortal? The Turritopsis dohrnii, also known as the "immortal jellyfish," can transform its body into a younger state through a process called transdifferentiation. This means it can essentially revert back to its polyp stage, which is the juvenile form of a jellyfish, and then grow back into an adultagain. This process can be repeated indefinitely, making Turritopsis dohrnii theoretically immortal.

Isn't that mind-blowing?
"""

# now we try this with a smaller model also
response = ollama.chat.completions.create(model='gemma3:270m', messages=[{"role": "user", "content": "Tell me a fun fact"}])
print(response.choices[0].message.content)

"""
Response:

Okay, here's a fun fact:

The Mona Lisa was created by Leonardo da Vinci.
"""
