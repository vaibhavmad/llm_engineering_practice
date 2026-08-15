# first lets recollect, what all we need to import
# openai 
# os
# dotenv
# json
# gradio
# sqlite3

from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import gradio as gr
import sqlite3

# IMPORTANT: We shall go step by step and keep commenting out the syntax that completes it's purpose

# next, we need to load open ai key and check if is working fine or not
load_dotenv(override=True)
openai_key = os.getenv("OPENAI_API_KEY")

# if openai_key.startswith('sk-proj'): #type: ignore
#     print('OPENAI KEY: OKAY')
# else:
#     print('OPENAI KEY: NOT OKAY')

# openai key is okay and loaded, next up, we create openai_client, which we will use to call the LLM
openai_client = OpenAI()

# next, we test if the client is working fine or not by sending a simple message
# response = openai_client.chat.completions.create(model='gpt-4.1-mini', messages=[{"role": "user", "content": "Tell a joke for an aspiring LLM engineer"}])
# print(response.choices[0].message.content)

# this is working fine, received response:
# Why did the large language model go to therapy? Because it had too many unresolved tokens!

# now, we define system message
system_message = "You are a helpful assistant for an airline called FlightAI. Your work is to politely respond to the users and in no more than one sentence. If you are not aware of the information being asked, please inform so to the user, do not deviate from this."

# next up, we create the db using sqlite3
# test it by printing the table and then commenting out the code for creation of table and addition of data to it
# flight_price = {
#     'delhi': "$299",
#     "mumbai": "$399",
#     "chennai": "$499",
#     "rome": "$599",
#     "toronto": "$699",
#     "london": "$799",
#     "paris": "$1129"
# }

# with sqlite3.connect('flight_ai_price.db') as conn:
#     cursor = conn.cursor()
    # cursor.execute("CREATE TABLE city_prices (city TEXT, price TEXT)")
    # for city, price in flight_price.items():
    #     cursor.execute("INSERT INTO city_prices VALUES(?, ?)", (city, price))

    # cursor.execute("SELECT * FROM city_prices")
    # print(cursor.fetchall())

# db created, table created, data added, validated, below output:
# [('delhi', '$299'), ('mumbai', '$399'), ('chennai', '$499'), ('rome', '$599'), ('toronto', '$699'), ('london', '$799'), ('paris', '$1129')]


# nextup, we create the function to fetch price information from the db
def get_price(city):
    with sqlite3.connect('flight_ai_price.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM city_prices WHERE city = ?", (city.lower(), ))
        price_details = cursor.fetchone()

    return f"Price for {price_details[0]} is {price_details[1]}" if price_details else "Unknown city, price not known"

# print(get_price('kjkjkjkjk'))
# function is working fine, output: Price for mumbai is $399, however, it should also return Unknown City, price not available, which we take up in the next session
# now the function returns for an unknown city also. So, this function is our tool. The LLM can run this to fetch price of return ticket to the destination city by passing in the destination city. We now need to create a json, so that LLM can understand when and how to use this function.

get_price_function = {
    "name": "get_price",
    "description": "Returns the price of a return ticket to the destination city",
    "parameters": {
        "type": 'object',
        "properties": {
            "city": {
                "type": "string",
                "description": "destination city for which return price is needed"
            }
        },
        "required": ["city"],
        "additionalProperties": False
    }
}


tools = [{"type": "function", "function": get_price_function}]

# print(tools)
# price function works fine, now we test this, if tool is being called and price is being returned by the llm or not

# response = openai_client.chat.completions.create(model="gpt-4.1-mini", messages=[{"role": "system", "content": system_message}, {"role": "user", "content": "What is the price for mumbai?"}], tools=tools) #type: ignore

# print(response)

"""
response:
ChatCompletion(id='chatcmpl-ED3MrWu6K1iXQ65wmWehx3EPJdhIZ', choices=[Choice(finish_reason='tool_calls', index=0, logprobs=None, message=ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=[ChatCompletionMessageFunctionToolCall(id='call_fSP2l9QCH10j8iZzbe2aeDO4', function=Function(arguments='{"city":"mumbai"}', name='get_price'), type='function')]))], created=1786779917, model='gpt-4.1-mini-2025-04-14', object='chat.completion', moderation=None, service_tier='priority', system_fingerprint='fp_b3e898ecd6', usage=CompletionUsage(completion_tokens=15, prompt_tokens=121, total_tokens=136, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cache_write_tokens=None, cached_tokens=0)))
"""

# Now we can see, that finish reason is tool_calls, function name is get_price and city is mumbai, which is as per our query. So, this is working fine till here.