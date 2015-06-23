#!/usr/bin/env python

import sys
import os
from pyspark import SparkContext
from PIL import Image
import numpy as np

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

out_dir = 'preprocessed'
try:
    os.mkdir(out_dir)
except OSError, e:
    pass 

IMAGE_SIZE = 256

def resize_image_file(file):
    file = file.strip()
    im = Image.open(file)
    imarr = np.array(im)
    sq_im = make_square(imarr)
    cr_im = crop(sq_im)
    re_im = resize_image(cr_im, IMAGE_SIZE)
    outfile = out_dir + '/' + os.path.basename(file)
    re_im.save(outfile, 'JPEG')
    return 1

def main(image_files):
    sc = SparkContext( appName="Resize Images")
    sc.parallelize(image_files).map(resize_image_file).count()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "The program needs a filename which lists the image files"
        exit()

    file = sys.argv[1]
    images = []
    with open(file) as f:
        for line in f:
            images.append(line.strip())
    main(images)

