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

    return f"Price for {price_details[0]} is {price_details[1]}"

# print(get_price('mumbai'))
# function is working fine, output: Price for mumbai is $399, however, it should also return Unknown City, price not available, which we take up in the next session
    

