'''
Preprocessing for images
  The general steps are:
  1) load the image and pad the shorter side with black to make it square
  2) find the center and radius of the eye and trim a square to that size
  3) normalize each color channel to zero mean, unit variance
  4) resize the image to 128x128 and 256x256 and save jpeg's
  (LATER) create 7 additional images for each size from rotations (90,180,270-deg) and flip and rotations (0,90,180,270-deg)
'''


import matplotlib.pyplot as plt  # for seeing plots, not for preprocessing

import numpy as np

from PIL import Image
import PIL

from skimage.transform import resize
from skimage.util import img_as_ubyte
from skimage.color import rgb2gray
from skimage import exposure

import glob


#plt.rc('image', cmap='gray')

#Opens image and converts to a numpy array
def make_img_array(path):
  img = Image.open(path)
  return np.asarray(img)


DIRECTORY = './Data/uniformsample_orig_04/'    # original images contained in this directory
#Create a list of tuples, image name and image path. Map the paths to array representation of the image
image_paths = glob.glob(DIRECTORY + "*.jpeg")
print("\nNumber of images to be processed from '%s': %d\n" % (DIRECTORY, len(image_paths)))
image_names = [jpeg[len(DIRECTORY):-5] for jpeg in image_paths]
image_list = zip(image_names, image_paths)

#print len(image_list)

count = 0

for img in image_list:

  count +=1
  #if count>1:
  #  break

  print("processing image number: %d\t\t(%s)" % (count,img[0]))
  #print img[0]
  im = make_img_array(img[1])

  # get height and width of the image
  ht =im.shape[0]
  wd = im.shape[1]
  #print "height = ",ht
  #print "width = ",wd

  # amount of padding needed to make a square image
  paddingamt = int(np.absolute(wd-ht)/2.0)

  # axis for concatenation
  concataxis = 1*(wd<ht)

  # make padding arrays
  if concataxis==0:
    padding = np.zeros((paddingamt, im.shape[1], im.shape[2]))
  else:
    padding = np.zeros((im.shape[0], paddingamt, im.shape[2]))

  #print "\noriginal image shape = ",im.shape
  #print "shape of padding = ",padding.shape

  # concatenate to make padded image
  paddedim = np.concatenate([padding, im, padding], axis=concataxis)/255.0

  #print "padded image shape = ",paddedim.shape

  # convert to grayscale
  paddedimgray = rgb2gray(paddedim)
  #print "Converted to grayscale"
  #print np.mean(paddedimgray)
  #plt.imshow(paddedimgray)
  #plt.show()


  # make any part of the image that is not (very close to) black, white
  whitened = np.zeros(paddedimgray.shape)
  whitened[paddedimgray>0.1]=255
  #print "Whitened"
  #plt.imshow(whitened)
  #plt.show()

  cntrrow = int(np.mean(np.where(whitened==255)[0]))
  cntrcol = int(np.mean(np.where(whitened==255)[1]))

  #print("Center of white area at (%d, %d)" % (cntrrow, cntrcol))

  d1 = np.max(np.where(whitened[cntrrow,:]==255))-np.min(np.where(whitened[cntrrow,:]==255))
  d2 = np.max(np.where(whitened[:,cntrcol]==255))-np.min(np.where(whitened[:,cntrcol]==255))
  radius = np.max([d1,d2])/2.0
  #print "radius = ",radius

  leftc = cntrcol-radius
  rightc = cntrcol+radius
  topr = cntrrow-radius
  bottomr = cntrrow+radius
  #print topr, bottomr
  #print leftc, rightc

  trimmedim = paddedim[topr:bottomr,leftc:rightc,:]
  
  #print "Trimmed"
  #plt.imshow(trimmedim)
  #plt.show()
  
  #print trimmedimgray.shape

  norm = np.zeros(trimmedim.shape)
  norm[:,:,0] = (trimmedim[:,:,0]-np.mean(trimmedim[:,:,0]))/np.std(trimmedim[:,:,0])
  norm[:,:,1] = (trimmedim[:,:,1]-np.mean(trimmedim[:,:,1]))/np.std(trimmedim[:,:,1])
  norm[:,:,2] = (trimmedim[:,:,2]-np.mean(trimmedim[:,:,2]))/np.std(trimmedim[:,:,2])

  resized128im = resize(norm, (128,128))
  resized256im = resize(norm, (256,256))
  
  #print "Normalized"
  #plt.imshow(norm)
  #plt.show()
  
  rescaled_256 = (255.0 / resized256im.max() * (resized256im - resized256im.min())).astype(np.uint8)
  im_256 = Image.fromarray(rescaled_256)
  impath_256 = "./Data/uniformsample_04_256rgb/"+img[0]+".jpeg"
  im_256.save(impath_256)

  rescaled_128 = (255.0 / resized128im.max() * (resized128im - resized128im.min())).astype(np.uint8)
  im_128 = Image.fromarray(rescaled_128)
  impath_128 = "./Data/uniformsample_04_128rgb/"+img[0]+".jpeg"
  im_128.save(impath_128)

