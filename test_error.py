"""
File : test_error.py

Author: Tim Schofield
Date: 21 May 2024

"""


import openai
from openai import OpenAI
from db import OPENAI_API_KEY


my_api_key = OPENAI_API_KEY          
client = OpenAI(api_key=my_api_key)


# chat mode does not suppor gpt-4o
try:
    #Make your OpenAI API request here
    response = client.completions.create(
        prompt="Hello world",
        model="gpt-3.5-turbo-instruct"
    )

    print(response)
  
except openai.APIError as e:
  #Handle API error here, e.g. retry or log
  print(f"OpenAI API returned an API Error: {e}")
  pass
except openai.APIConnectionError as e:
  #Handle connection error here
  print(f"Failed to connect to OpenAI API: {e}")
  pass
except openai.RateLimitError as e:
  #Handle rate limit error (we recommend using exponential backoff)
  print(f"OpenAI API request exceeded rate limit: {e}")
  pass