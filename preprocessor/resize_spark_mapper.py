#!/usr/bin/env python

import sys
import os
from pyspark import SparkContext
from PIL import Image
import numpy as np
import glob
import cPickle

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

CUR_DIR = '/root/W251_Project/preprocessor/'
IMAGE_SIZE = 256
TEST_OR_TRAIN = 'train'

def make_img_array(im_path):
    return np.array(Image.open(im_path))

def resize_image_file(file):
    file = file.strip()
    imarr = make_img_array(file)
    sq_im = make_square(imarr)
    cr_im = crop(sq_im)
    re_im = resize_image(cr_im, IMAGE_SIZE)
    outfile = CUR_DIR + TEST_OR_TRAIN + '_' + str(IMAGE_SIZE) + '/' + os.path.basename(file)
    re_im.save(outfile, 'JPEG')
    return 1

def save_images(dir):
    img_paths = glob.glob(dir + "/*.jpeg")
    img_list = map(make_img_array, img_paths)
    pfile = CUR_DIR + TEST_OR_TRAIN + '_' + str(IMAGE_SIZE) + '.cpickle' 
    f = open(pfile, 'wb')
    cPickle.dump(img_list, f)

def main(image_files):
    sc = SparkContext( appName="Resize Images")
    sc.parallelize(image_files).map(resize_image_file).count()

    #read all the resized images into an array to save as a pickled object
    out_dir = CUR_DIR + TEST_OR_TRAIN + '_' + str(IMAGE_SIZE)
    save_images(out_dir)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Usage: $SPARK_HOME/bin/spark-submit resize_spark_mapper.py <test_or_train> <image_size> <directory_with_image_files>'
        exit()

    TEST_OR_TRAIN = sys.argv[1]
    IMAGE_SIZE = int(sys.argv[2])
    img_dir = sys.argv[3]
    images = glob.glob(img_dir + "/*.jpeg")
    try:
        out_dir = CUR_DIR + TEST_OR_TRAIN + '_' + str(IMAGE_SIZE)
        os.mkdir(out_dir)
    except OSError, e:
        pass
    main(images)
