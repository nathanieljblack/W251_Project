#!/usr/bin/env python

import sys
import os
from PIL import Image
import numpy as np
import glob
import csv

def make_square(im):
    new_h = min(im.shape[0], im.shape[1])
    new_w = new_h
    h_low = 0
    h_high = im.shape[0]-1
    w_low = 0
    w_high = im.shape[1]-1
    if (new_h < im.shape[0]):
        h_low = (im.shape[0] - new_h)/2
        h_high = im.shape[0] - h_low
    if (new_w < im.shape[1]):
        w_low = (im.shape[1] - new_w)/2
        w_high = im.shape[1] - w_low - 1

    new_img = im[h_low:h_high, w_low:w_high, :]
    return new_img

def crop(im):
    h = int(im.shape[0]*0.05)
    w = int(im.shape[1]*0.05)
    new_img = im[w:-w, h:-h, :]
    return new_img

def resize_image(im, img_size):
    img = Image.fromarray(im)
    return img.resize((img_size, img_size))

def make_img_arr(im):
    return np.array(im).ravel().tolist()

def add_to_csv(arr, label=None):
    f = csvfile_p
    if label != None:
        arr = label + arr
    for i, j in enumerate(arr):
        if i == (len(arr) - 1):
            f.write(str(j) + "\n")
        else:
            f.write(str(j) + ",")

out_dir = 'preprocessed'
try:
    os.mkdir(out_dir)
except OSError, e:
    pass

TEST_OR_TRAIN = sys.argv[1]
IMAGE_SIZE = int(sys.argv[2])
img_dir = sys.argv[3]
images = glob.glob(img_dir + "/*.jpeg")

csvfile = TEST_OR_TRAIN + '_' + str(IMAGE_SIZE) + '.csv'
csvfile_p = open(csvfile, 'w')

d = {}
if TEST_OR_TRAIN == 'train':
    #Make image mapping
    reader = csv.reader(open('trainLabels.csv', 'r'))
    #Make dictionary from each row in the CSV (skip first row)
    for k,v in reader:
        if k != "image":
            d[k] = int(v)

for file in images:
    file = file.strip()
    im = Image.open(file)
    imarr = np.array(im)
    sq_im = make_square(imarr)
    cr_im = crop(sq_im)
    re_im = resize_image(cr_im, IMAGE_SIZE)
    outfile = out_dir + '/' + os.path.basename(file)
    re_im.save(outfile, 'JPEG')
    img_arr = make_img_arr(re_im)
    img_label = None
    if TEST_OR_TRAIN == 'train':
        img_label = [d[os.path.basename(file)[:-5]]]
    add_to_csv(img_arr, img_label)

csvfile_p.close()
