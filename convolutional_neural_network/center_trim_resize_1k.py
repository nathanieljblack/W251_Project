'''
  Center all images and resize to 1024 x 1024 for faster preprocessing
'''


#import matplotlib.pyplot as plt  # for seeing plots, not for preprocessing

import numpy as np

from PIL import Image
import PIL

from skimage.transform import resize
from skimage.util import img_as_ubyte
from skimage import util
from skimage.color import rgb2gray

import glob

from time import time


#plt.rc('image', cmap='gray')

def make_img_array(path):
  '''
    Input: path to image jpeg
    Returns: image as a numpy array
  '''
  img = Image.open(path)
  return np.asarray(img)

def pad_image(img):
  '''
  Input: image as numpy array
  Returns: image padded with black to make square
  '''
  
  # get height and width of the image
  ht =img.shape[0]
  wd = img.shape[1]
  #print "height = ",ht
  #print "width = ",wd
  
  # amount of padding needed to make a square image
  paddingamt = int(np.absolute(wd-ht)/2.0)
  
  # axis for concatenation
  concataxis = 1*(wd<ht)
  
  # make padding arrays
  if concataxis==0:
    padding = np.zeros((paddingamt, img.shape[1], img.shape[2]))
  else:
    padding = np.zeros((img.shape[0], paddingamt, img.shape[2]))
  
  #print "\noriginal image shape = ",im.shape
  #print "shape of padding = ",padding.shape
  
  # concatenate to make padded image
  return np.concatenate([padding, img, padding], axis=concataxis)


def make_gray(img):
  '''
  Input: image as numpy array
  Returns: grayscale version of image
  '''
  # convert to grayscale
  gray = rgb2gray(img)
  #print "Converted to grayscale"
  #print np.mean(gray)
  #plt.imshow(gray)
  #plt.show()
  return gray


def whiten_eye(img):
  '''
  Input: grayscale version of image as numpy array
  Returns: image with eye whitened to 255 uniformly
  '''
  # make any part of the image that is not (very close to) black, white
  whitened = np.zeros(img.shape)
  
  ## *********** The best value here for seaprating the eye part of the image from the black border varies
  ##              somewhat because of the wide variations in lighting and image quality
  ##             If the value is too high, then the image will not be processed and the name
  ##              will be saved to a list in the imagesnotprocessed.txt file (if this value is too low, then the
  ##              image will be processed but some of the eye may be cut off)
  ##             The easiest way to make sure that all of the images are processed is to set this value
  ##              relatively high (~30) then iteratively process the few images that are very dark
  ##              (and are not processed) with lower and lower values
  threshold_value_for_black = 10
  
  
  whitened[img>threshold_value_for_black]=255
  #print "Whitened"
  #plt.imshow(whitened)
  #plt.show()
  return whitened


def find_center(img):
  '''
  Input: image with eye whitened to 255 uniformly
  Returns: coordinates of center of eye
  '''
  cntrrow = int(np.mean(np.where(img==255)[0]))
  cntrcol = int(np.mean(np.where(img==255)[1]))
  
  #print("Center of white area at (%d, %d)" % (cntrrow, cntrcol))
  return (cntrrow, cntrcol)

def find_radius(img, center):
  '''
  Input: image with eye whitened to 255 uniformly
  Returns: coordinates of center of eye
  '''

  d1 = np.max(np.where(img[center[0],:]==255))-np.min(np.where(img[center[0],:]==255))
  d2 = np.max(np.where(img[:,center[1]]==255))-np.min(np.where(img[:,center[1]]==255))
  radius = np.max([d1,d2])/2.0
  #print "radius = ",radius
  return radius


def center_and_trim_image(img):
  '''
  Input: image as numpy array, padded with black to be square
  Returns: image centered on eye and trimmed tight to larger diameter of eye
  '''
  
  tmp_img = make_gray(img)
  tmp_img = whiten_eye(tmp_img)
  center = find_center(tmp_img)
  radius = find_radius(tmp_img, center)

  leftc = center[1]-radius
  rightc = center[1]+radius
  topr = center[0]-radius
  bottomr = center[0]+radius
  #print topr, bottomr
  #print leftc, rightc
  
  return img[topr:bottomr,leftc:rightc,:]


def main():
  source_dir = './train_mod/'    # original images contained in this directory

  dest_dir = './train_mod_1k/'   # preprocessed images to be stored in this directory

  image_paths = glob.glob(source_dir + "*.jpeg")
  print("\nNumber of images to be processed from '%s': %d\n" % (source_dir, len(image_paths)))
  image_names = [jpeg[len(source_dir):-5] for jpeg in image_paths]
  image_list = zip(image_names, image_paths)

  #print len(image_list)

  count = 0

  fpath_notprocessed = 'imagesnotprocessed_'+str(time())+".txt"
  f_notprocessed = open(fpath_notprocessed, 'w')

  for im in image_list:
  
    count +=1
    #if count>5:
    #  break

    print("processing image number: %d\t\t(%s)" % (count,im[0]))
    image = make_img_array(im[1])

    image = pad_image(image)

    try:
      image = center_and_trim_image(image)
    except:
      f_notprocessed.write(im[0]+'\n')
      continue

    try:
      image = resize(image, (1024,1024))
    except:
      f_notprocessed.write(im[0]+'\n')
      continue

    image = Image.fromarray(image.astype(np.uint8))
    impath = dest_dir+im[0]+"_1k.jpeg"
    image.save(impath)

  f_notprocessed.close()

if __name__ == "__main__":
  main()

