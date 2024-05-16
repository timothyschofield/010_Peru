"""
File : main_ocr.py

Tim Schofield

12 December 2023

This uses GPT-4o to OCR images from a local folder
and process them into JSON

WARNING: If you put the actual API key in this file, Git will not allow it to be pushed
Git calls it a "secret"

In Linux
export OPENAI_API_KEY="<the openai key>" 
printenv OPENAI_API_KEY 
 
On Windows
setx OPENAI_API_KEY <the openai key>
type "set" to see the

Then access the API key thus:
my_api_key = os.environ["OPENAI_API_KEY"]

2024-05-14
Moved to Linux

Need a metric
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
https://stackoverflow.com/questions/17388213/find-the-similarity-metric-between-two-strings

"""
from db import OPENAI_API_KEY
from helper_functions import encode_image
from openai import OpenAI
import base64
import requests
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

try:
  my_api_key = OPENAI_API_KEY          
  client = OpenAI(api_key=my_api_key)
except Exception as ex:
    print("Exception:", ex)
    exit()

MODEL = "gpt-4o"

# These are used to measure success/loss
keys = ["'collector'", "'collector number'", "'date'", "'family'", "'genus'", "'species'", "'altitude'", "'location'", 
        "'latitude'", "'longitude'", "'language'", "'country'", "'description'", "'barcode number'"]
keys_concatenated = ", ".join(keys)

# The last sentence about letter "K" really helps a lot - experiment with more prompts like this
request = f"Please read this hebarium sheet and extract {keys_concatenated}. Barcode numbers begin with 'K'. Please return in JSON format with {keys_concatenated} as keys" 

image_folder = Path("source_images/")
image_path_list = list(image_folder.glob("*.jpg"))
print(image_path_list)

print("####################################### START OUTPUT ######################################")

for image_path in image_path_list:

  try:

    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {my_api_key}"
    }
    
    # payload is in JSON format
    payload = {
        "model": MODEL,
        "messages": [
          {
            "role": "user",
            "content": [
              {"type": "text", "text": request},
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}"
                }
              }
            ]
          }
        ],
        "max_tokens": 300
    }

    ocr_output = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    #print(type(ocr_output)) <class 'requests.models.Response'>
    #print("apparent_encoding", ocr_output.apparent_encoding)  # utf-8
    #print("encoding", ocr_output.encoding)                    # utf-8
    #print("json object", ocr_output.json())                   # a JSON formated object

    print("\n########################## OCR OUTPUT " + str(image_path) + " ##########################\n")
    json_returned = ocr_output.json()['choices'][0]['message']['content']
    print(json_returned)

  
  except Exception as ex:
      print("Exception:", ex)

print("####################################### END OUTPUT ######################################")










