
import base64
# Function to base64 encode an image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
from datetime import datetime
# e.g. 2024-05-18T06-53-26
def get_file_timestamp():
  current_dateTime = datetime.now()
  year = current_dateTime.year
  month = current_dateTime.month
  day = current_dateTime.day
  hour = current_dateTime.hour
  minute = current_dateTime.minute
  second = current_dateTime.second
  return f"{year}-{month:02}-{day:02}T{hour:02}-{minute:02}-{second:02}"
    
import json
def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True
 
import torch
def get_torch_cuda_info():
  print("-----------------------")
  print("torch version", torch.__version__)
  print("CUDA avaliable", torch.cuda.is_available())
  print("torch.CUDA version", torch.version.cuda)
  print("-----------------------")

  if torch.cuda.is_available():
      print('__CUDNN VERSION:', torch.backends.cudnn.version())   # CUDA Deep Neural Networks
      print('__Number CUDA Devices:', torch.cuda.device_count())
      print('__CUDA Device Name:',torch.cuda.get_device_name(0))
      print('__CUDA Device Total Memory [GB]:',torch.cuda.get_device_properties(0).total_memory/1e9)
      print("-----------------------")

  # Setup device agnostic code
  if torch.cuda.is_available():
      device = "cuda"
  else:
      device = "cpu"
  print(f"device: {device}")  
      

import pandas as pd
from pathlib import Path
def create_and_save_dataframe(output_list, key_list_with_logging, output_path_name):
  output_df = pd.DataFrame(output_list)
  output_df = output_df[key_list_with_logging]  # Bring reorder dataframe to bring source url and error column to the front
  output_path = Path(output_path_name)
  with open(output_path, "w") as f:
    output_df.to_csv(f, index=False)
    
    
    
    
    