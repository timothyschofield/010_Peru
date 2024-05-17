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

index_col = "source_images"

# These are used to measure success/loss
keys = ["'collector'", "'collector number'", "'date'", "'family'", "'genus'", "'species'", "'altitude'", "'location'", 
        "'latitude'", "'longitude'", "'language'", "'country'", "'description'", "'barcode number'"]
keys_concatenated = ", ".join(keys)

print("##########################")

json_returned1 = {
  "collector": "J. Wood 1",
  "collector number": "2181",
  "date": "31 Mar 2010",
  "family": "Liliaceae",
  "genus": "Milligania",
  "species": "densiflora",
  "altitude": "829 m",
  "location": "Lyell Highway, King William Pass, Franklin - Gordon Wild Rivers National Park",
  "latitude": "-42° 14' 44.5\" S",
  "longitude": "145° 46' 05.6\" E",
  "language": "English",
  "country": "Australia",
  "description": "Boggy heath/huttonii-baugainiony. Soak-hewn organic soil: c. 30cm, slope with poor drainage. Associated species: Actinotus suffocatus, Carpha alpina, Gahnia grandis, Xyris spp, Baumea tetragona, Empodisma minus. Herb. 70cm high. Rhizome 6cm at pole, with 8cm frond leaf 12cm root-fibres. Leaves flat, 70mm at the blade, stem with a pink flush: leaves with more green mid-rid than surrounding blade.",
  "barcode number": "K003610655"
}

# The last sentence about letter "K" really helps a lot - experiment with more prompts like this
prompt = f"Please read this hebarium sheet and extract {keys_concatenated}. Barcode numbers begin with 'K'. Please return in JSON format with {keys_concatenated} as keys" 

image_folder = Path("source_images/")
image_path_list = list(image_folder.glob("*.jpg"))
print(image_path_list)

output_path = Path("output/out.csv")

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
        "max_tokens": 300
    }

    ocr_output = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # print(type(ocr_output)) <class 'requests.models.Response'>
    # print("apparent_encoding", ocr_output.apparent_encoding)  # utf-8
    # print("encoding", ocr_output.encoding)                    # utf-8
    print("json object ****", ocr_output.json(), "****")                   # a JSON formated object

    print(f"\n########################## OCR OUTPUT {image_path} ##########################\n")
    json_returned = ocr_output.json()['choices'][0]['message']['content']
    
    # Clean up the returned JSON
    json_returned = json_returned.split("json")[1:]     # remove leading ```json
    json_returned = "".join(json_returned)
    json_returned = json_returned.split("```")[:-1]     # remove the last ``` - It must be the precise quote character 
    json_returned = "".join(json_returned)
    #print("clean1 ****",json_returned,"****")

    dict_returned = eval(json_returned) # JSON -> Dict
    dict_returned["source_image"] = str(image_path)
  
  
    json_returned2 = {
    "collector": "J. Wood 2",
    "collector number": "2181",
    "date": "31 Mar 2010",
    "family": "Liliaceae",
    "genus": "Milligania",
    "species": "densiflora",
    "altitude": "829 m",
    "location": "Lyell Highway, King William Pass, Franklin - Gordon Wild Rivers National Park",
    "latitude": "-42° 14' 44.5\" S",
    "longitude": "145° 46' 05.6\" E",
    "language": "English",
    "country": "Australia",
    "description": "Boggy heath/huttonii-baugainiony. Soak-hewn organic soil: c. 30cm, slope with poor drainage. Associated species: Actinotus suffocatus, Carpha alpina, Gahnia grandis, Xyris spp, Baumea tetragona, Empodisma minus. Herb. 70cm high. Rhizome 6cm at pole, with 8cm frond leaf 12cm root-fibres. Leaves flat, 70mm at the blade, stem with a pink flush: leaves with more green mid-rid than surrounding blade.",
    "barcode number": "K003610655"
    }
  
    dict_returned2 = dict(json_returned2)
    dict_returned2[index_col] = str("source_images/K008888855.jpg")
    df1 = pd.DataFrame([dict_returned, dict_returned2])
    
  #### oe for loop
    
  # bring the source_images column to the from and make it the index
  df1 = df1[[index_col] + [x for x in df1.columns if x != index_col]]
  df1.set_index(index_col)
    
  print(df1)
  
  df1.to_csv(output_path, index=False)

  print("########################")

except Exception as ex:
    print("Exception:", ex)

print("####################################### END OUTPUT ######################################")










