#!/usr/bin/env python

import sys
import os
from skimage.transform import resize
from skimage import io

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
    re_im = resize(im, (img_size, img_size))
    return re_im


out_dir = 'preprocessed'
try:
    os.mkdir(out_dir)
except OSError, e:
    print e

IMAGE_SIZE = 512

for file in sys.stdin:
    file = file.strip()
    im = io.imread(file)
    sq_im = make_square(im)
    cr_im = crop(sq_im)
    re_im = resize_image(cr_im, IMAGE_SIZE)
    outfile = out_dir + '/' + os.path.basename(file)
    io.imsave(outfile, re_im)
    sys.stdout.write("Success\t1\n")
