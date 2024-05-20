"""
File : easy_ocr.py

Author: Tim Schofield
Date:2024-05-19

Export to json file

https://medium.com/@adityamahajan.work/easyocr-a-comprehensive-guide-5ff1cb850168
https://github.com/JaidedAI/EasyOCR
https://www.jaided.ai/easyocr/


"""
import easyocr
import cv2                          # Computer Vision 2 library
import matplotlib.pyplot as plt
import torch
from helper_functions import get_torch_cuda_info, get_file_timestamp
from pathlib import Path

get_torch_cuda_info()

file_name = "K004470351_100_label_only_nasty_hw"
file_name = "K000663552_100_label_only"
file_name = "K000663552"

source_path = Path(f"source_easyocr/{file_name}.jpg")
print(f"{source_path=}")

output_path =  Path(f"output_easyocr/{file_name}_out_{get_file_timestamp()}.jpg")
print(f"{output_path=}")

reader = easyocr.Reader(['en'], gpu=True)

image = cv2.imread(str(source_path))
result = reader.readtext(image)

print(result)
Total = []
for (bbox, text, prob) in result:
    Total.append(text)
    (tl, tr, br, bl) = bbox
    tl = (int(tl[0]), int(tl[1]))
    tr = (int(tr[0]), int(tr[1]))
    br = (int(br[0]), int(br[1]))
    bl = (int(bl[0]), int(bl[1]))
    cv2.rectangle(image, tl, br, (0, 255, 0), 1)
    cv2.putText(image, text, (tl[0], tl[1] - 2),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0),1)
plt.rcParams['figure.figsize'] = (16,16)
plt.imshow(image)
plt.show()

plt.imsave(output_path, image)
print(' '.join(Total).split("SHIP TO", 1)[1])




















