"""
File : main_ocr.py

Author: Tim Schofield
Date: 12 December 2023

This uses GPT-4o to OCR images from a local folder
and process them into JSON. Max image size is 20M. max_tokens returned 4096

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

ocr_output response_code:500
RAW ocr_output **** {'error': {'message': 'The server had an error processing your request. Sorry about that! You can retry your request, 
or contact us through our help center at help.openai.com if you keep seeing this error. (
  Please include the request ID req_80fe5b982069b0fd2d5d2d2ccca7080c in your email.)', 'type': 'server_error', 'param': None, 'code': None}} ****

 
Must handel when an error is returned
json object **** {'error': {'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, 
read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.', 'type': 'insufficient_quota', 'param': None, 'code': 'insufficient_quota'}} ****
    
"""
import openai
from openai import OpenAI

from db import OPENAI_API_KEY
from peru_url_list import URL_PATH_LIST
from helper_functions_peru import encode_image, get_file_timestamp, is_json, create_and_save_dataframe
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

prompt = (
  f"Read this hebarium sheet and extract all the text you can see."
  f"The hebarium sheet may use Spanish words and Spanish characters."
  f"You are going to return all of this text in a JSON field called 'verbatim'"
  f"Go through the text you have extracted and return data in JSON format with {keys_concatenated} as keys."
  f"Translate the 'specimenNotesSpanish' field into English and return it in the 'specimenNotesEnglish' field."
  f"If you can not find latitude and longitude data, estimate it from location information and store it in the latitude and longitude fields in degrees, minutes and seconds format."
  f"If you find only one collector name, put that name in both the collector and collector1 fields"
  f"If you find more than one collector name, put all the names in the collector field and then put the individual collectors (or groups of collectors) in fields collector1 to collector4."
  f"Do not wrap the JSON data in JSON markers."
  f"If you find no value for a key never return 'null', return 'none'."
)


batch_size = 50 # saves every 50
time_stamp = get_file_timestamp()

count = 0
project_name = "Peru"

source_type = "url" # url or offline
if source_type == "url":
  image_path_list = URL_PATH_LIST[:1]
else:
  image_folder = Path("input_gpt/")
  image_path_list = list(image_folder.glob("*.jpg"))

print(f"Number to process:{len(image_path_list)}")

print("####################################### START OUTPUT ######################################")
try:
  
  for image_path in image_path_list:
    
    print(f"\n########################## OCR OUTPUT {image_path} ##########################\n")
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
        "logprobs": False,
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
        "max_tokens": 4096   # The max_tokens that can be returned. 'usage': {'prompt_tokens': 1126, 'completion_tokens': 300, 'total_tokens': 1426}, 'system_fingerprint': 'fp_927397958d'}
    } 
    
    num_tries = 3
    for i in range(num_tries):
      print("Making Request =====================================================")
      ocr_output = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
      response_code = ocr_output.status_code
      if response_code == 200:
        break
      else:
        print(f"======= 200 not returned. Trying request again number {i} ===========================")
        print(f"{str(ocr_output.json())}")

    response_code = ocr_output.status_code
    print(f"ocr_output response_code:{response_code}")
    
    if response_code != 200:
      # Didn't even get to ChatGPT
      print("RAW ocr_output ****", ocr_output.json(),"****")                   
      dict_returned = eval(str(empty_output_dict))
      dict_returned['verbatim'] = str(ocr_output.json())
      error_message = "200 NOT returned from GPT"
      print(error_message)
    else:
      # We got to ChatGPT
      json_returned = ocr_output.json()['choices'][0]['message']['content']
      
      # It would be nice to be able to mockup json_returned for testing
      # json_returned = '{"name":"tim", "age":"64"}'
      
      # HERE I DEAL WITH SOME FORMATS THAT CREATE INVALID JSON
      
      # 1) Turn to raw with "r" to avoid the escaping quotes problem
      json_returned = fr'{json_returned}'
      print(f"content****{json_returned}****")
      
      # 2) Sometimes null still gets returned, even though I asked it not to
      if "null" in json_returned: 
        json_returned = json_returned.replace("null", "'none'")
      
      # 3) Occasionaly the whole of the otherwise valid JSON is returned with surrounding square brackets like '[{"text":"tim"}]'
      # or other odd things like markup '''json and ''' etc.
      # This removes everything prior to the opening "{" and after the closeing "}"
      open_brace_index = json_returned.find("{")
      json_returned = json_returned[open_brace_index:]
      close_brace_index = json_returned.rfind("}")
      json_returned = json_returned[:close_brace_index+1]
      
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
      print(f"WRITING BATCH:{count}")
      output_path_name = f"output_gpt/{project_name}_{time_stamp}-{count}.csv"
      create_and_save_dataframe(output_list=output_list, key_list_with_logging=key_list_with_logging, output_path_name=output_path_name)

  #################################### eo for loop

  # For safe measure and during testing where batches are not batch_size
  print(f"WRITING BATCH:{count}")
  output_path_name = f"output_gpt/{project_name}_{time_stamp}-{count}.csv"
  create_and_save_dataframe(output_list=output_list, key_list_with_logging=key_list_with_logging, output_path_name=output_path_name)
  
except openai.APIError as e:
  #Handle API error here, e.g. retry or log
  print(f"TIM: OpenAI API returned an API Error: {e}")
  pass

except openai.APIConnectionError as e:
  #Handle connection error here
  print(f"TIM: Failed to connect to OpenAI API: {e}")
  pass

except openai.RateLimitError as e:
  #Handle rate limit error (we recommend using exponential backoff)
  print(f"TIM: OpenAI API request exceeded rate limit: {e}")
  pass

print("####################################### END OUTPUT ######################################")










