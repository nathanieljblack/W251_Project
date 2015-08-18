import os
import numpy as np
from PIL import Image
import csv
import sys

image = sys.argv[1]

#Make image mapping
reader = csv.reader(open('trainLabels.csv', 'r'))
d = {}
#Make dictionary from each row in the CSV (skip first row)
for k,v in reader:
    if k != "image":
        d[k] = int(v)

#DIRECTORY = "/Users/nathanielblack/Downloads/sample/"
IMAGE_SIZE = 64

def make_img_array(path):
    img = Image.open(path)
    return np.array(img.resize((IMAGE_SIZE,IMAGE_SIZE))).ravel().tolist()

img_label = [d[image[:-5]]]
img_arr = make_img_array(image)
out = img_label + img_arr
for i, j in enumerate(out):
	if i == (len(out) - 1):
		sys.stdout.write(str(j) + "\n")
	else:
		sys.stdout.write(str(j) + ",")