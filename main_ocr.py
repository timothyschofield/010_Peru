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
temperature = 0

ocr_output response_code:500
RAW ocr_output **** {'error': {'message': 'The server had an error processing your request. Sorry about that! You can retry your request, 
or contact us through our help center at help.openai.com if you keep seeing this error. (
  Please include the request ID req_80fe5b982069b0fd2d5d2d2ccca7080c in your email.)', 'type': 'server_error', 'param': None, 'code': None}} ****

 
    1. Must handel when an error is returned
    json object **** {'error': {'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, 
    read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.', 'type': 'insufficient_quota', 'param': None, 'code': 'insufficient_quota'}} ****
    
    2. Must write outputs to disk in batches
    
"""
import openai
from openai import OpenAI

from db import OPENAI_API_KEY
from peru_url_list import URL_PATH_LIST
from helper_functions import encode_image, get_file_timestamp, is_json
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

# MODEL = "gpt-4-vision-preview"
MODEL = "gpt-4o"

# For Kew
keys_in_quotes_list = ["'verbatim'", "'barcode number'", "'collector'", "'collector number'", "'date'", "'family'", "'genus'", "'species'", "'altitude'", "'location'", 
        "'latitude'", "'longitude'", "'language'", "'country'", "'description'"]

# For Peru
keys_in_quotes_list = ["'verbatim'", "'barcode'", "'collector'", "'collectorNumber'", "'collector1'", "'collector2'", "'collector3'", "'collector4'", "'collectionDate'", "'collectionYYYY'", "'collectionMM'", 
  "'collectionDD'", "'family'", "'genus'", "'species'", "'taxon_name'", "'altitude'", "'altitudeUnit'", "'country'", 
  "'stateProvinceTerritory'", "'location'", "'latitude'", "'longitude'", "'language'", "'specimenNotesSpanish'", "'specimenNotesEnglish'"]

keys_concatenated = ", ".join(keys_in_quotes_list)

# Make an empty output template for none-json output errors
key_list = [key.replace("'", '') for key in keys_in_quotes_list] # Get rid of surrounding double quotes
empty_output_dict = dict([])
for this_key in key_list:
  empty_output_dict[this_key] = "none"

# This adds columns to the output csv that we were not searching for in the input text
source_image_col = "source_image"
error_col = "ERROR"
key_list_with_logging = [source_image_col, error_col] + key_list

output_list = []

# The last sentence about letter "K" really helps a lot - experiment with more prompts like this
# NOTE: The line f"Do not wrap the JSON codes in JSON markers." gets rid of the leading '''json which you get otherwise
prompt = (
  f"Read this hebarium sheet and extract {keys_concatenated}."
  f"Barcode numbers begin with 'K'."
  f"Concentrate all your efforts on reading the text."
  f"Return the data in JSON format with {keys_concatenated} as keys."
  f"Do not wrap the JSON data in JSON markers."
  f"If you find no value for a key, return 'none'."
  )

prompt = (
  f"Read this hebarium sheet and extract all the text you can see."
  f"The hebarium sheet may use Spanish words and Spanish characters."
  f"Concentrate all your efforts on reading the text."
  )

prompt = (
  f"Read this hebarium sheet and extract all the text you can see."
  f"The hebarium sheet may use Spanish words and Spanish characters."
  f"You are going to return all of this text in a JSON field called 'verbatim'"
  f"Go through the text you have extracted and return data in JSON format with {keys_concatenated} as keys."
  f"Translate the 'specimenNotesSpanish' field into English and return it in the 'specimenNotesEnglish' field."
  f"Do not wrap the JSON data in JSON markers."
  f"If you find no value for a key never return 'null', return 'none'."
)

source_type = "url" # url or offline
batch_size = 50

start_at = 900

if source_type == "url":
  image_path_list = URL_PATH_LIST[start_at:]
else:
  image_folder = Path("input_gpt/")
  image_path_list = list(image_folder.glob("*.jpg"))

print(f"Number to process:{len(image_path_list)}")

time_stamp = get_file_timestamp()
count = start_at

print("####################################### START OUTPUT ######################################")
try:
  
  for image_path in image_path_list:
    
    count+=1
    print(f"count: {count}")
    
    error_message = "OK"

    if source_type == "url":
      url_request = image_path
    else:
      base64_image = encode_image(image_path)
      url_request = f"data:image/jpeg;base64,{base64_image}"

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
              {
                "type": "text",
                "temperature": "0.2",
                "text": prompt
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": url_request
                }
              }
            ]
          }
        ],
        "max_tokens": 2000   # max_tokens that can be returned? 'usage': {'prompt_tokens': 1126, 'completion_tokens': 300, 'total_tokens': 1426}, 'system_fingerprint': 'fp_927397958d'}
    } 
    
    print(f"\n########################## OCR OUTPUT {image_path} ##########################\n")
    
    ocr_output = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    response_code = ocr_output.status_code
    print(f"ocr_output response_code:{response_code}")
    
    if response_code != 200:
      print("RAW ocr_output ****", ocr_output.json(),"****")                   
      dict_returned = eval(str(empty_output_dict))
      dict_returned['verbatim'] = str(ocr_output.json())
      error_message = "200 NOT returned from GPT"
      print(error_message)
    else:
      json_returned = ocr_output.json()['choices'][0]['message']['content']
      print(f"content****{json_returned}****")

      if "null" in json_returned: 
        print("null detected in json_returned and replace with 'none'")
        json_returned = json_returned.replace("null", "'none'")
      
      if is_json(json_returned):
        dict_returned = eval(json_returned) # JSON -> Dict
      else:
        dict_returned = eval(str(empty_output_dict))
        dict_returned['verbatim'] = str(json_returned)
        error_message = "JSON NOT RETURNED FROM GPT"
        print(error_message)
      
    dict_returned[source_image_col] = str(image_path)       # Insert the image source file name into output
    dict_returned[error_col] = str(error_message)           # Insert error message into output

    output_list.append(dict_returned) # Create list first, then turn into DataFrame
  
    if count % batch_size == 0:
      output_df = pd.DataFrame(output_list)
      output_df = output_df[key_list_with_logging]  # Bring reorder dataframe to bring source url and error column to the front
      
      output_path_name = f"output_gpt/out_{time_stamp}-{count}.csv"
      print(f"WRITING BATCH:{count}")
      output_path = Path(output_path_name)
      with open(output_path, "w") as f:
        output_df.to_csv(f, index=False)
  
  #################################### eo for loop

  # For safe measure
  output_df = pd.DataFrame(output_list)
  output_df = output_df[key_list_with_logging]  # Bring reorder dataframe to bring source url and error column to the front
  
  output_path_name = f"output_gpt/out_{time_stamp}-{count}.csv"
  print(f"WRITING BATCH:{count}")
  output_path = Path(output_path_name)
  with open(output_path, "w") as f:
    output_df.to_csv(f, index=False)
  
  
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

print("####################################### END OUTPUT ######################################")










