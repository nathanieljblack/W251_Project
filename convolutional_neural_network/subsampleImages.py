'''
  subsample from training data for images of eyes with most severe diabetic retinopathy (labeled 4) and no signs   of the disease
'''

import numpy as np
import pandas as pd
import csv
from subprocess import call


#np.random.seed(0)


def main():

  labels = list()
  with open("./Data/trainLabels.csv", "rb") as f:
    reader = csv.reader(f)
    for row in reader:
      labels.append(row)

  labels = pd.DataFrame(labels[1:], columns=['name','level'])
  labels['level'] = labels['level'].astype(int)

  print labels['level'].value_counts()
  label_counts = labels['level'].value_counts()
  N = sum(label_counts)
  #print "N = ", N
  num_classes = len(label_counts)
  #print "num_classes = ", num_classes

  # some code for setting probabilities to sample evenly from all 5 classes
  '''
  labels['p'] = np.nan
  for i in range(num_classes):
    labels.loc[labels['level'] == i, 'p'] = (1.0/(num_classes*label_counts[i]))
    labels.loc[labels['level'] == i, 'p'] = p[i]
  print sum(labels['p'])
  sample = np.random.choice(np.asarray(labels['name']), size = 4000, replace=False, p = np.asarray(labels['p']))
  '''


  p = np.zeros(num_classes)

  for i in [0,4]:
    p[i] = (1.0/(2*label_counts[i]))

  for i in [0,4]:

    sample = np.random.choice(np.asarray(labels.loc[labels['level'] == i, 'name']), size = label_counts[4], replace=False)
    #print len(sample)

    for im in sample:
      cl = "scp root@50.97.227.70:/root/train_all/"+im+".jpeg ./Data/uniformsample_orig_04/"
      #count +=1
      #print str(count)+") "+cl
      call(cl, shell=True)




if __name__ == "__main__":
  main()
