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
    conn.close()

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
# also, keeping the above response in file, since we will be needing it later to look at components, when we build info extraction.

# next up we build handle_tool_calls function
# this function, must return response for all tool calls. So, for this, we also iterate over tool calls using for loop in this function.

# before that, just for curiosity, I have not yet seen a response, where multiple tool calls have been returned by the LLM, lets try that also


# response = openai_client.chat.completions.create(model="gpt-4.1-mini", messages=[{"role": "system", "content": system_message}, {"role": "user", "content": "What is the price for mumbai and rome?"}], tools=tools) #type: ignore

# print(response)

"""
Response:
ChatCompletion(id='chatcmpl-ED3YlBzsj8g1bSKrR4K4x3yCYQOpG', choices=[Choice(finish_reason='tool_calls', index=0, logprobs=None, message=ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=[ChatCompletionMessageFunctionToolCall(id='call_nXFaWN7EBvia7HWDnxHSTvQ3', function=Function(arguments='{"city": "mumbai"}', name='get_price'), type='function'), ChatCompletionMessageFunctionToolCall(id='call_S4yT2GWCdtbZPDXPEhcK7fD3', function=Function(arguments='{"city": "rome"}', name='get_price'), type='function')]))], created=1786780655, model='gpt-4.1-mini-2025-04-14', object='chat.completion', moderation=None, service_tier='priority', system_fingerprint='fp_b3e898ecd6', usage=CompletionUsage(completion_tokens=45, prompt_tokens=124, total_tokens=169, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cache_write_tokens=None, cached_tokens=0)))
"""

# great, we can see a list after tool call, with two tool calls for each, mumbai and rome.

# now, on receiving this, we only need to send tool_calls to the handle_tool_calls function, so that can be extracted as: response.choices[0].message.tool_calls
# let's validate this also
# response = openai_client.chat.completions.create(model="gpt-4.1-mini", messages=[{"role": "system", "content": system_message}, {"role": "user", "content": "What is the price for mumbai and rome?"}], tools=tools) #type: ignore

# print(response.choices[0].message.tool_calls)

"""
Response:
[ChatCompletionMessageFunctionToolCall(id='call_rr6UnPNeJSjxkjSZcynr63vI', function=Function(arguments='{"city": "mumbai"}', name='get_price'), type='function'), ChatCompletionMessageFunctionToolCall(id='call_M1HkXibvPmvpoG46lHKv7xws', function=Function(arguments='{"city": "rome"}', name='get_price'), type='function')]
"""

# validated, we treat this as our input for the handle_tool_calls function

# next, we need to extract the following info from this tool call:
# id, function arguments and function name
# we validate this also

# response = openai_client.chat.completions.create(model="gpt-4.1-mini", messages=[{"role": "system", "content": system_message}, {"role": "user", "content": "What is the price for mumbai and rome?"}], tools=tools) #type: ignore
# message = response.choices[0].message.tool_calls

# for tool_call in message:
#     print(tool_call)
#     print(tool_call.id)
#     print(tool_call.function)
#     print(tool_call.function.arguments)
#     print(tool_call.function.name)


# def handle_tool_calls(message):
#     responses = []
#     for tool_call in message:
#         if tool_call.function.name == 'get_price':
#             arguments = json.loads(tool_call.function.arguments)
#             city_name = arguments['city']
#             price_details = get_price(city_name)
#             responses.append({
#                 "role": "tool",
#                 "content": f"price for {city_name} is {price_details}",
#                 "tool_call_id": tool_call.id
#             })

#     return responses

# let's validate if this function is working fine

# response = openai_client.chat.completions.create(model="gpt-4.1-mini", messages=[{"role": "system", "content": system_message}, {"role": "user", "content": "What is the price for mumbai and rome?"}], tools=tools) #type: ignore
# message = response.choices[0].message.tool_calls

# print(handle_tool_calls(message))

"""
respose:
[{'role': 'tool', 'content': 'price for mumbai is Price for mumbai is $399', 'tool_call_id': 'call_3fKRVsY3IftuxXrBlNdlAWuo'}, {'role': 'tool', 'content': 'price for rome is Price for rome is $599', 'tool_call_id': 'call_DG4UjfbIA0i5PZZE9WgVvVCp'}]
"""
# one glitch, we have in content repition, lets correct it

def handle_tool_calls(message):
    responses = []
    for tool_call in message:
        # now, there can be multiple tool calls in a message from the LLM. Hence, we check for each tool call using if else
        if tool_call.function.name == 'get_price':
            arguments = json.loads(tool_call.function.arguments)
            city_name = arguments['city']
            price_details = get_price(city_name)
            responses.append({
                "role": "tool",
                "content": price_details,
                "tool_call_id": tool_call.id
            })

    return responses

# let's validate again

# response = openai_client.chat.completions.create(model="gpt-4.1-mini", messages=[{"role": "system", "content": system_message}, {"role": "user", "content": "What is the price for mumbai and rome?"}], tools=tools) #type: ignore
# message = response.choices[0].message.tool_calls

# print(handle_tool_calls(message))

"""
response:
[{'role': 'tool', 'content': 'Price for mumbai is $399', 'tool_call_id': 'call_5VJIf0hRVTd4Lj1V9Y4k26rs'}, {'role': 'tool', 'content': 'Price for rome is $599', 'tool_call_id': 'call_Qh7py4btlBT9ZMMt3CE42BAM'}]
"""
# awesome, this works fine. now lets move ahead with the building the chat function. This function will take messages and history.
# message is the user query and history is what we get from gradio

def chat(message, history):
    # first let's clean the history
    history = [{"role": h["role"], "content": h["content"]} for h in history]

    # now lets define the messages, we first pass the system prompt, then history and finally the user prompt
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]

    # now, since messages are defined, we send the first message to LLM, for this, we create response
    response = openai_client.chat.completions.create(model="gpt-4.1-mini", messages=messages, tools=tools) #type: ignore

    # now, there are two options, the response will either contain a tool call or a response for the user, therefore, we must has a while block that checks the code till tool_calls is the finish_reason and finally, we return the response
    
    # under while loop, er pass on the message from LLM to the handle_tool_calls function and save it's response
    while response.choices[0].finish_reason == "tool_calls":
        llm_message = response.choices[0].message.tool_calls
        tool_response = handle_tool_calls(llm_message)
        # now, we need to append the tool_calls response that we received from the LLM in the messages, and since, we need to share the same format as other segments of the messages, we append response.choices[0].message to messages, since message contains 'role', 'content' and 'tool_calls together'
        messages.append(response.choices[0].message) #type: ignore
        # and now we extend the response that we have received from the tool to the messages, since it is also a list and we can add that to the same instead of appending
        messages.extend(tool_response)
        # now, we have the tool response added to the messages, we now need to send it back to the llm for its consumption
        # also, we still add tool call to this, since, the response can come back again with tool calls, so telling the llm, what all tools exist, is a must at this step
        response = openai_client.chat.completions.create(model="gpt-4.1-mini", messages=messages, tools=tools) #type: ignore


    return response.choices[0].message.content


# finally, we run this in gradio and test it
gr.ChatInterface(chat).launch(share=True)
# let's run the program and check if it works fine or not, I will be pasting the conversation below
"""
user: Hi
assisstant: Hello! How can I assist you with your flight needs today?

user: what all can you help me with?
assisstant: I can assist you with flight bookings, provide ticket prices, answer travel-related questions, and offer information about destinations.

# checking if it answers info that is not available
user: what is the temperature in London right now?
assisstant: I'm sorry, but I don't have access to current weather information.

user: okay, what is the price for a flight to London?
assisstant: The price for a return ticket to London is $799.

user: And what about to Paris?
assisstant: The price for a return ticket to Paris is $1129.

# checking multiple tool calls execution
user: awesome, now, I want you to first check the price for Paris and only if it is more than 1000 USD, check the price for Chennai and let me know
assisstant: The price for a return ticket to Paris is $1129, which is more than $1000, and the price for a return ticket to Chennai is $499.

# checking price for city not available in db
user: great, and what is the price for Honolulu?
assisstant: I'm sorry, but I don't have the price information for flights to Honolulu.
"""
