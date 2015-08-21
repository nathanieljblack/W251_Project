'''
Normalize colors to zero mean, unit variance and resize then save all images as cPickle
'''

import numpy as np

from PIL import Image

from skimage.transform import resize

from glob import glob

from time import time

import cPickle



def getImagesList(dir):
  '''
    Input: directory containing jpeg images, named by subject number and left or right eye
    Returns: a list of tuples as (subject number, image name, path to image)
  '''
  if not dir[-1]=="/":
    dir = dir+"/"
  image_paths = glob(dir + "*.jpeg")
  print("\nNumber of images to be processed from '%s': %d\n" % (dir, len(image_paths)))
  image_names = list()
  image_numbers = list()
  for jpeg in image_paths:
    levels = jpeg.split("/")
    filename = levels[len(levels)-1]
    parts = filename.replace(".","_").split("_")
    image_names.append(str(parts[0])+"_"+parts[1])
    image_numbers.append(int(parts[0]))
  image_list = zip(image_numbers, image_names, image_paths)
  return image_list


def make_img_array(path):
  '''
    Input: path to image jpeg
    Returns: image as a numpy array
  '''
  img = Image.open(path)
  return np.asarray(img)


def color_norm(img_array):
  '''
    Input: image as numpy array
    Returns: image array with each channel normalized to zero mean, unit variance
  '''
  
  norm = np.zeros(img_array.shape)
  
  norm[:,:,0] = (img_array[:,:,0]-np.mean(img_array[:,:,0]))/np.std(img_array[:,:,0])
  norm[:,:,1] = (img_array[:,:,1]-np.mean(img_array[:,:,1]))/np.std(img_array[:,:,1])
  norm[:,:,2] = (img_array[:,:,2]-np.mean(img_array[:,:,2]))/np.std(img_array[:,:,2])
  
  return norm


def main():

  source_dir = './Data/uniformsample_04_1k_mirror_rot/'    # original images contained in this directory
  image_list = getImagesList(source_dir)
  
  pickle_file = './Data/uniformsample_04_1k_mirror_rot_hp.cpickle' # pickle of processed images
  
  count = 0
  
  image_pickle_list = list()

  for img in image_list:

    count +=1
    #if count>1:
      #break

    #print("processing image number: %d\t\t(%s)" % (count, img[1]))
    
    img_array = make_img_array(img[2])
    
    img_array = color_norm(img_array)
    
    size = 128  # set image size for input to preprocessor here
    img_array = resize(img_array, (size, size))
    
    image_pickle_list.append((img[1], img_array))

  cPickle.dump(image_pickle_list, open(pickle_file, 'wb'), protocol=cPickle.HIGHEST_PROTOCOL)
  


if __name__ == "__main__":
  main()

