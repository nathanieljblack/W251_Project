#!/usr/bin/env python

import sys
import os
from pyspark import SparkContext
from PIL import Image
import numpy as np
import glob
import cPickle
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

CUR_DIR = '/root/W251_Project/preprocessor/'
IMAGE_SIZE = 256
TEST_OR_TRAIN = 'train'

def make_img_array(im_path):
    return np.array(Image.open(im_path))

def make_img_list(im_path):
    return np.array(Image.open(im_path)).ravel().tolist()

def resize_image_file(file):
    file = file.strip()
    imarr = make_img_array(file)
    sq_im = make_square(imarr)
    cr_im = crop(sq_im)
    re_im = resize_image(cr_im, IMAGE_SIZE)
    outfile = CUR_DIR + TEST_OR_TRAIN + '_' + str(IMAGE_SIZE) + '/' + os.path.basename(file)
    re_im.save(outfile, 'JPEG')
    return 1

def add_to_csv(f, arr, label):
    print type(label)
    if type(label) == list:
        print 'list'
        arr = label + arr
    else:
        print 'not list'
        arr = [label] + arr
    for i, j in enumerate(arr):
        if i == (len(arr) - 1):
            f.write(str(j) + "\n")
        else:
            f.write(str(j) + ",")

def save_images_csv(dir):
    pfile = CUR_DIR + TEST_OR_TRAIN + '_' + str(IMAGE_SIZE) + '.csv' 
    f = open(pfile, 'wb')
    img_paths = glob.glob(dir + "/*.jpeg")
    for path in img_paths:
        img = make_img_list(path)
        img_label = None
        if TEST_OR_TRAIN == 'train':
            try:
                img_label = [d[os.path.basename(path)[:-5]]]
            except KeyError:
                continue
        else:
            img_label = os.path.basename(path)[:-5]
        add_to_csv(f, img, img_label)

def save_images(dir):
    img_paths = glob.glob(dir + "/*.jpeg")
    img_list = map(make_img_array, img_paths)
    pfile = CUR_DIR + TEST_OR_TRAIN + '_' + str(IMAGE_SIZE) + '.cpickle' 
    f = open(pfile, 'wb')
    cPickle.dump(img_list, f)

d = {}
if TEST_OR_TRAIN == 'train':
    #Make image mapping
    reader = csv.reader(open('trainLabels.csv', 'r'))
    #Make dictionary from each row in the CSV (skip first row)
    for k,v in reader:
        if k != "image":
            d[k] = int(v)

def main(image_files):
    sc = SparkContext( appName="Resize Images")
    sc.parallelize(image_files).map(resize_image_file).count()

    #read all the resized images into an array to save as a pickled object
    #out_dir = CUR_DIR + TEST_OR_TRAIN + '_' + str(IMAGE_SIZE)
    #save_images(out_dir)

    #read all the resized images into an array to save as a csv file
    out_dir = CUR_DIR + TEST_OR_TRAIN + '_' + str(IMAGE_SIZE)
    save_images_csv(out_dir)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Usage: $SPARK_HOME/bin/spark-submit resize_spark_mapper.py <test_or_train> <image_size> <directory_with_image_files>'
        exit()

    TEST_OR_TRAIN = sys.argv[1]
    IMAGE_SIZE = int(sys.argv[2])
    img_dir = sys.argv[3]
    images = glob.glob(img_dir + "/*.jpeg")
    try:
        os.mkdir(CUR_DIR)
    except OSError:
        pass
    try:
        out_dir = CUR_DIR + TEST_OR_TRAIN + '_' + str(IMAGE_SIZE)
        os.mkdir(out_dir)
    except OSError:
        pass
    main(images)
