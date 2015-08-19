'''
  Convolutional neural network for diabetic retinopathy image classification
  
  CNN code is modified from the nolearn tutorial at https://github.com/dnouri/nolearn/blob/master/docs/notebooks/CNN_tutorial.ipynb
'''

#import matplotlib.pyplot as plt #%pylab inline
import numpy as np
import pandas as pd
from glob import glob
from PIL import Image
import cPickle
import csv

from lasagne.layers import DenseLayer
from lasagne.layers import InputLayer
from lasagne.layers import DropoutLayer
from lasagne.layers import Conv2DLayer
from lasagne.layers import MaxPool2DLayer
from lasagne.nonlinearities import softmax
from lasagne.updates import adam, nesterov_momentum
from lasagne.layers import get_all_params

from nolearn.lasagne import NeuralNet
from nolearn.lasagne import TrainSplit
from nolearn.lasagne import objective

import theano
from theano import tensor as T
from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams

from theano.tensor.nnet.conv import conv2d
from theano.tensor.signal.downsample import max_pool_2d

print theano.config.device
print theano.config.floatX


IMAGE_SIZE = 128

def make_labels_array(path):
  '''
    Input: path to training data labels csv file
    Returns: list of labels as IMAGE_NAME, LABEL
  '''
  raw_labels = []
  with open(path, "rb") as f:
    reader = csv.reader(f)
    for row in reader:
      raw_labels.append(row)
  return raw_labels


def make_dataframe(images_path):
  '''
    Input: path to training data labels csv file
    Returns: list of labels as IMAGE_NAME, LABEL
  '''
  image_list = cPickle.load(open(images_path, 'rb'))
  return pd.DataFrame(image_list, columns = ['name', 'image_array'])

def load_labels(labels_path):
  '''
    Input: path to training labels file
    Returns: pandas data frame containing labels with columns 'name' and 'level'
  '''
  raw_labels = make_labels_array(labels_path)
  raw_labels = pd.DataFrame(raw_labels[1:], columns=['name','level'])
  raw_labels['level'] = raw_labels['level'].astype(np.int32)
  return raw_labels

def get_subjects_in_test(data):
  '''
    Input: all labeled data
    Returns: list of subjects to include in test data set
  '''
  subject_nums = pd.Series(data['number']).unique()
  num_subjects = len(subject_nums)
  
  num_in_test = int(0.2*num_subjects)
  
  return np.random.choice(subject_nums, size=num_in_test, replace=False)

def make_train_and_test_sets(images_path, labels_path):
  '''
    Because we have right and left eye images for many subjects and we have created synthetic data from existing
    data, we need to ensure that each subject is in either training or test to prevent leakage of information
    from training to testing.
    
    Inputs: paths to preprocessed images pickle and to data labels
    Returns: training and test set data and labels
  '''
  images_df = make_dataframe(images_path)
  
  all_labels = load_labels(labels_path)
  all_labels.loc[all_labels['level']==4, 'level']=1
  
  data = pd.merge(images_df, all_labels, on='name')
  data['number'] = data['name'].str.split('_').str.get(0)
  
  subjects_in_test = get_subjects_in_test(data)
  
  test_data_df = data.loc[data['number'].isin(subjects_in_test), 'image_array']
  print test_data_df.shape
  
  test_data = np.zeros((test_data_df.count(),data['image_array'][0].shape[0], data['image_array'][0].shape[1], data['image_array'][0].shape[2]))
  for i in range(test_data_df.shape[0]):
    test_data[i,:,:,:] = np.asarray(test_data_df)[i]
  print "test data shape: ",test_data.shape
  
  test_labels = np.asarray(data.loc[data['number'].isin(subjects_in_test), 'level'])

  train_data_df = data.loc[~data['number'].isin(subjects_in_test),'image_array']
  
  train_data = np.zeros((train_data_df.count(),data['image_array'][0].shape[0], data['image_array'][0].shape[1], data['image_array'][0].shape[2]))
  for i in range(train_data_df.shape[0]):
    train_data[i,:,:,:] = np.asarray(train_data_df)[i]
  print "train data shape: ",train_data.shape

  train_labels = np.asarray(data.loc[~data['number'].isin(subjects_in_test),'level'])
  
  print_label_counts = True
  if print_label_counts:
    print "Label counts"
    print "0: ",(sum(train_labels==0)+sum(test_labels==0))
    print "1: ",(sum(train_labels==1)+sum(test_labels==1))
    print "2: ",(sum(train_labels==2)+sum(test_labels==2))
    print "3: ",(sum(train_labels==3)+sum(test_labels==3))
    print "4: ",(sum(train_labels==4)+sum(test_labels==4))
    print "\nLabel counts in test data"
    print "0: ",sum(test_labels==0)
    print "1: ",sum(test_labels==1)
    print "2: ",sum(test_labels==2)
    print "3: ",sum(test_labels==3)
    print "4: ",sum(test_labels==4)

  return train_data, train_labels, test_data, test_labels

def main():
  pickle_file = '/mnt/Data/uniformsample_04_1k_mirror_rot_128x128_norm.cpickle'
  labels_csvfile = '/mnt/Data/trainLabels.csv'

  train_data, train_labels, test_data, test_labels = make_train_and_test_sets(pickle_file, labels_csvfile)

  train_data = train_data.reshape(-1, 3, IMAGE_SIZE, IMAGE_SIZE)
  train_data = train_data.astype('float32')
  test_data = test_data.reshape(-1, 3, imageWidth, imageWidth)
  test_data = test_data.astype('float32')

  numFeatures = train_data[1].size
  numTrainExamples = train_data.shape[0]
  print 'Features = %d' %(numFeatures)
  print 'Train set = %d' %(numTrainExamples)

  print "training data shape: ", train_data.shape
  print "training labels shape: ", train_labels.shape

  layers0 = [
             (InputLayer, {'shape': (None, X.shape[1], X.shape[2], X.shape[3])}),
           
             (Conv2DLayer, {'num_filters': 32, 'filter_size': 3}),
             (Conv2DLayer, {'num_filters': 32, 'filter_size': 3}),
             (Conv2DLayer, {'num_filters': 32, 'filter_size': 3}),
             (MaxPool2DLayer, {'pool_size': 2}),
           
             (Conv2DLayer, {'num_filters': 64, 'filter_size': 3}),
             (Conv2DLayer, {'num_filters': 64, 'filter_size': 3}),
             (MaxPool2DLayer, {'pool_size': 2}),
           
             (Conv2DLayer, {'num_filters': 128, 'filter_size': 3}),
             (Conv2DLayer, {'num_filters': 128, 'filter_size': 3}),
             (MaxPool2DLayer, {'pool_size': 2}),
           
             (DenseLayer, {'num_units': 600}),
             (DropoutLayer, {}),
             (DenseLayer, {'num_units': 600}),
           
             (DenseLayer, {'num_units': 2, 'nonlinearity': softmax}),
             ]

  def regularization_objective(layers, lambda1=0., lambda2=0., *args, **kwargs):
    ''' from nolearn MNIST CNN tutorial'''
    # default loss
    losses = objective(layers, *args, **kwargs)
    # get the layers' weights, but only those that should be regularized
    # (i.e. not the biases)
    weights = get_all_params(layers[-1], regularizable=True)
    # sum of absolute weights for L1
    sum_abs_weights = sum([abs(w).sum() for w in weights])
    # sum of squared weights for L2
    sum_squared_weights = sum([(w ** 2).sum() for w in weights])
    # add weights to regular loss
    losses += lambda1 * sum_abs_weights + lambda2 * sum_squared_weights
    return losses

  clf = NeuralNet(
                  layers=layers0,
                  max_epochs=5,
                 
                  # optimization method
                  update=nesterov_momentum,
                  update_momentum=0.9,
                  update_learning_rate=0.0002,
                 
                  objective=regularization_objective,
                  objective_lambda2=0.0025,
                 
                  train_split=TrainSplit(eval_size=0.1),
                  verbose=1,
                
                  )

  # load parameters from pickle file to continue training from previous epochs or smaller network
  #clf.load_params_from('params1.pickle')
  #clf.initialize()

  for i in range(100):
    print '******************************  ',i,'  ******************************'

    clf.fit(train_data, train_labels)

    clf.save_params_to('params2.pickle')

    preds = clf.predict(test_data)
    #print sum(preds)
    print "Test data accuracy: ", 1.0*sum(preds==test_labels)/test_labels.shape[0]


if __name__ == "__main__":
  main()



