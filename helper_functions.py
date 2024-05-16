import base64


# Function to base64 encode an image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    