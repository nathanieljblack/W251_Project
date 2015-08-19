'''
  Copy images to multiple VS's for trivially parallelizable preprocessing
  
  Command line options: -D or -distribute :    distribute images from local directory to VS's
                        -C or -collect    :    collect images from VS's to local directory
'''

from glob import glob
import sys
from subprocess import call
import numpy as np



def getImagesList(dir):
  '''
    Input: directory containing jpeg images, named by subject number and left or right eye
    Returns: a list of tuples as (subject number, image name, path to image)
  '''
  if not dir[-1]=="/":
    dir = dir+"/"
  image_paths = glob(dir + "*.jpeg")
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


def distribute_images(image_list, server_names, dest_dir):
  '''
    Inputs: image_list = list of image numbers, names, and paths returned from getImagesList(dir)
            server_names = list of names of VS's to send images to
            dest_dir = directory on remote VS in which to place image
    Copies images to remote directories for parallel processing
  '''

  count = 0
  num_servers = len(server_names)
  for im in image_list:
    
    cl = "scp "+im[2]+" "+" root@"+server_names[im[0]%num_servers]+":"+dest_dir+"/"+im[1]+".jpeg"
    call(cl, shell=True)
    count += 1
    if count%200==0:
      print count

  return None


def collect_images(server_names, distr_dir, local_dir):
  '''
    Inputs: image_list = list of names of VS's to collect images from
            distr_dir = directories on remote VS's that contain images
            local_dir = directory to copy images into
    Copies images from remote directories
  '''
  
  for vs in server_names:
    
    cl = "scp "+"root@"+vs+":"+distr_dir+"/* "+"local_dir"
    call(cl, shell=True)

  return None



def main():

  distr_or_collect = sys.argv[1]
  print distr_or_collect
  distr=False
  collect=False
  if distr_or_collect=='-D' or distr_or_collect=='-distribute':
    distr = True
  elif distr_or_collect=='-C' or distr_or_collect=='-collect':
    collect = True
  else:
    "Enter '-distribute' or '-collect'"
    exit()

  try:
    source_dir = sys.argv[2]
  except IndexError:
    if distr:
      source_dir = './train_all/'
      print "loading and copying images from "+source_dir
    else:
      source_dir = './train_mod'
      print "collecting images from "+source_dir

  try:
    dest_dir = sys.argv[3]
  except IndexError:
    if distr:
      dest_dir = './train_mod'
      print "copying images to "+dest_dir
    else:
      dest_dir = './train_1k'
      print "collecting images into "+dest_dir

  server_names = ['trainimages1', 'trainimages2', 'trainimages3', 'trainimages4']
  
  if distr:
    image_list = getImagesList(source_dir)
    distribute_images(image_list, server_names, dest_dir)

  if collect:
    collect_images(server_names, source_dir, dest_dir)


if __name__ == "__main__":
  main()
