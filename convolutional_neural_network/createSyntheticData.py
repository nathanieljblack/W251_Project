'''
Save three rotations (90, 180, and 270 degrees) and mirror of images with rotations
'''

from PIL import Image
from glob import glob



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


def saverotations(path, name, dir, flip=False):
  '''
    Inputs: path = path to image
            name = image name (subjectNumber_leftOrRight)
            dir = directory to save rotations into
            flip = boolean, whether image should be flipped (mirrored) before saving rotations
    Saves jpeg files for rotated images
  '''
  img = Image.open(path)
  deg = [90.0,180.0,270.0]
  if flip:
    img = img.transpose(Image.FLIP_LEFT_RIGHT)
    deg = [0.0, 90.0,180.0,270.0]
  for a in deg:
    rotated = img.rotate(a)
    if not dir[-1]=="/":
      dir = dir+"/"
    if flip:
      path = dir+name+"_1k_mirror_"+str(int(a))+"deg.jpeg"
    else:
      path = dir+name+"_1k_nomirror_"+str(int(a))+"deg.jpeg"
    rotated.save(path)
  return None



def main():

  source_dir = './Data/uniformsample_04_1k/'    # original images contained in this directory
  image_list = getImagesList(source_dir)
  
  count = 0

  for img in image_list:

    count +=1
    #if count>1:
      #break

    print("processing image number: %d\t\t(%s)" % (count,img[1]))
    
    dest_dir = './Data/uniformsample_04_1k_mirror_rot/'

    saverotations(img[2], img[1], dest_dir, flip=False)

    saverotations(img[2], img[1], dest_dir, flip=True)


if __name__ == "__main__":
  main()

