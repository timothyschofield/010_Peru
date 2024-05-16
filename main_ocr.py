"""
File : main_ocr.py

Tim Schofield

12 December 2023

This uses GTP4-V and GTP4 to OCR images from a local folder
and process them into JSON

WARNING: If you put the actual API key in here Git will not allow it to be pushed
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


request = "Please read this hebarium sheet and extract collector and collector number, date, family, genus, species, altitude, latitude, longitude, location, country, description, language and the barcode number which begins with the letter 'K'"

image_folder = Path("source_images/")
print("source folder",image_folder.is_dir())

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
    
    payload = {
        "model": "gpt-4-vision-preview",
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

    print("\n########################## OCR OUTPUT " + str(image_path) + " ##########################\n")
    input_to_json = ocr_output.json()['choices'][0]['message']['content']
    print(input_to_json)

    # Now convert to JSON
    json_output = client.chat.completions.create(
        model="gpt-4", 

        messages=[
            {"role": "system", "content": "First, delete all occurances of '\n  '. Format this as JSON where 'Collector', 'Collector number', 'Date', 'Family', 'Genus', 'Species', 'Altitude', 'Location', 'Latitude', 'Longitude', 'Language', 'Country', 'Description' and 'Barcode number' are keys"},
            {"role": "user", "content": str(input_to_json)}
            ]
    )

    print("\n##################### JSON " + str(image_path) + " ###############################\n")

    print(json_output.choices[0].message.content)
    print("#######################################################################################")
    print("#######################################################################################\n")
    
  except Exception as ex:
      print("Exception:", ex)

print("####################################### END OUTPUT ######################################")










