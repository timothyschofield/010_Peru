"""
File : main_ocr.py

Author: Tim Schofield
Date: 12 December 2023

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

Need a metric
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
https://stackoverflow.com/questions/17388213/find-the-similarity-metric-between-two-strings

startTime = time.perf_counter()

The last field returned in the JSON is:
'usage': {'prompt_tokens': 1126, 'completion_tokens': 300, 'total_tokens': 1426}, 'system_fingerprint': 'fp_927397958d'}
This can be used for accumulating usage information

You uploaded an unsupported image. Please make sure your image is below 20 MB in size and is of one the following formats: ['png', 'jpeg', 'gif', 'webp']

"""
from db import OPENAI_API_KEY
from helper_functions import encode_image, get_file_timestamp, is_json
from openai import OpenAI
import base64
import requests
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from datetime import datetime

try:
  my_api_key = OPENAI_API_KEY          
  client = OpenAI(api_key=my_api_key)
except Exception as ex:
    print("Exception:", ex)
    exit()

MODEL = "gpt-4o"

index_col = "source_image"

# These are used to measure success/loss
keys = ["'collector'", "'collector number'", "'date'", "'family'", "'genus'", "'species'", "'altitude'", "'location'", 
        "'latitude'", "'longitude'", "'language'", "'country'", "'description'", "'barcode number'"]
keys_concatenated = ", ".join(keys)







output_list = []

# The last sentence about letter "K" really helps a lot - experiment with more prompts like this
# NOTE: The line f"Do not wrap the JSON codes in JSON markers." gets rid of the leading '''json which you get otherwise
prompt = (
  f"Read this hebarium sheet and extract {keys_concatenated}."
  f"Barcode numbers begin with 'K'."
  f"Concentrate all your efforts on reading the text."
  f"Return in JSON format with {keys_concatenated} as keys."
  f"Do not wrap the JSON codes in JSON markers."
  f"Do not return 'null' return 'none'."
  )

"""
prompt = (
  f"Read this hebarium sheet and extract all the text you can see."
  f"Concentrate all your efforts on reading the text."
  f"Translate from Portuguese into English where appropriate."
  )
"""

image_folder = Path("source_images/")
image_path_list = list(image_folder.glob("*.jpg"))
print(image_path_list)

output_path_name = f"output/out_{get_file_timestamp()}.csv"
output_path = Path(output_path_name)


print("####################################### START OUTPUT ######################################")
try:
   
  for image_path in image_path_list:

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
              {"type": "text", "text": prompt},
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}"
                }
              }
            ]
          }
        ],
        "max_tokens": 2000   # max_tokens that can be returned? 'usage': {'prompt_tokens': 1126, 'completion_tokens': 300, 'total_tokens': 1426}, 'system_fingerprint': 'fp_927397958d'}
    } 

    ocr_output = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # print(type(ocr_output)) <class 'requests.models.Response'>
    # print("apparent_encoding", ocr_output.apparent_encoding)  # utf-8
    # print("encoding", ocr_output.encoding)                    # utf-8
    # print("json object ****", ocr_output.json(), "****")                   # a JSON formated object

    print(f"\n########################## OCR OUTPUT {image_path} ##########################\n")
    json_returned = ocr_output.json()['choices'][0]['message']['content']
    print(f"content****{json_returned}****")
    
    print("here1")
    
    
    # SOMETIMES STILL RETURNS "null"
    
    print("here2")
    #if is_json(json_returned):
      
      
    dict_returned = eval(json_returned) # JSON -> Dict
    print("here3")
    dict_returned[index_col] = str(image_path) # Insert the image source file name
    
    output_list.append(dict_returned) # Create list first, then turn into DataFrame

     
  #################################### eo for loop
  
  # print("output_list", output_list)
  output_df = pd.DataFrame(output_list)
  
  # bring the source_image column to the front and make it the index
  output_df = output_df[[index_col] + [x for x in output_df.columns if x != index_col]]
  output_df.set_index(index_col)
    
  print(output_df)
  
  output_df.to_csv(output_path, index=False)
  

except Exception as ex:
    print("Exception:", ex)

print("####################################### END OUTPUT ######################################")










