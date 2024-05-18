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
    
    
    
    
    
    
    
    
    
    
    
    
    