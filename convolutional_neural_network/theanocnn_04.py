'''
  Convolutional neural network for diabetic retinopathy image classification
  
  neural network code is modified from example code by Daniel Percival, MIDS W207, Live Session lab
  
  
  Command line to run on gpu:
       THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 python theanocnn_04.py
'''



import numpy as np
import pandas as pd
#from sklearn.metrics import classification_report
from glob import glob
import cPickle
import csv
from PIL import Image

import theano 
from theano import tensor as T
from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams
from theano.tensor.nnet.conv import conv2d
from theano.tensor.signal.downsample import max_pool_2d


print theano.config.device
print theano.config.floatX

# for theano debug
#theano.config.optimizer='None'
#theano.config.exception_verbosity='high'


#np.random.seed(0)


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


def binarizeY(data, numLabels):
    '''
      Inputs: training data labels and the number of different labels
      Returns: binarized version of the labels as array of zeros for each label with a one at position of correct category
    '''
    binarized_data = np.zeros((data.size,numLabels))
    for j in range(0,data.size):
        feature = data[j:j+1]
        i = feature.astype(np.int32)
        binarized_data[j,i]=1
    return binarized_data


def split_testdata_for_predict(test_data, test_labels, num_splits):
  '''
    Predictions on the whole test data is too much for the gpu memory, so split the test data to make predictions for smaller chunks
    Inputs: test data, test labels, and number of chunks to split the test data into
    Returns: list of test data chunks
  '''
  split_idx = int(test_data.shape[0]/4.0)
  test_data_splits_list = list()
  test_labels_splits_list = list()
  for i in range(num_test_data_splits):
    idx1 = i*split_idx
    if (i+2)*split_idx > test_data.shape[0]:
      idx2 = test_data.shape[0]
    else:
      idx2 = (i+1)*test_data_split_idx
    test_data_splits_list.append(test_data[idx1:idx2])
    test_labels_splits_list.append(test_labels[idx1:idx2])
  return test_data_splits_list, test_labels_splits_list




def main():


  pickle_file = './Data/uniformsample_04_1k_mirror_rot_128x128_norm.cpickle'
  labels_csvfile = './Data/trainLabels.csv'

  train_data, train_labels, test_data, test_labels = make_train_and_test_sets(pickle_file, labels_csvfile)


  train_labels_b = binarizeY(train_labels, numLabels = 2)
  test_labels_b = binarizeY(test_labels, numLabels = 2)
  numClasses = train_labels_b[1].size
  print 'Classes = %d' %(numClasses)


  numFeatures = train_data[1].size
  numTrainExamples = train_data.shape[0]
  numTestExamples = test_data.shape[0]
  print 'Features = %d' %(numFeatures)
  print 'Train set = %d' %(numTrainExamples)
  print 'Test set = %d' %(numTestExamples)

  train_data = train_data.reshape(-1, 3, IMAGE_SIZE, IMAGE_SIZE)
  #print train_data.shape
  test_data = test_data.reshape(-1, 3, IMAGE_SIZE, IMAGE_SIZE)

  train_data = train_data.astype('float32')
  train_labels_b = train_labels_b.astype('float32')
  
  num_test_data_splits = 4
  test_data_splits_list, test_labels_splits_list = split_testdata_for_predict(test_data, test_labels, num_test_data_splits)

  ## Define Network architecture
  numHiddenNodes = 600
  patchWidth = 3
  patchHeight = 3

  featureMapsLayer1 = 16
  featureMapsLayer2 = 32
  featureMapsLayer3 = 64
  featureMapsLayer4 = 128

  # Initialize convolution layer weights
  w_1 = theano.shared(np.asarray((np.random.randn(featureMapsLayer1, 3, patchWidth, patchHeight)),dtype='float32')*2+1)
  w_2 = theano.shared(np.asarray((np.random.randn(*(featureMapsLayer1, featureMapsLayer1, patchWidth, patchHeight))*.01),dtype='float32')*4+1)
  w_3 = theano.shared(np.asarray((np.random.randn(featureMapsLayer2, featureMapsLayer1, patchWidth, patchHeight)),dtype='float32')*4+1)
  w_4 = theano.shared(np.asarray((np.random.randn(featureMapsLayer3, featureMapsLayer2, patchWidth, patchHeight)),dtype='float32')*4+1)
  w_5 = theano.shared(np.asarray((np.random.randn(featureMapsLayer4, featureMapsLayer3, patchWidth, patchHeight)),dtype='float32')*4+1)

  # Initialize dense layer weights
  w_6 = theano.shared(np.asarray((np.random.randn(*(featureMapsLayer4 * 7 * 7, numHiddenNodes))*.01),dtype='float32'))
  w_7 = theano.shared(np.asarray((np.random.randn(*(numHiddenNodes, numClasses))*.01),dtype='float32'))

  params = [w_1, w_2, w_3, w_4, w_5, w_6, w_7]


  X = T.tensor4(dtype='float32')
  Y = T.matrix(dtype='float32')

  srng = RandomStreams()
  def dropout(X, p=0.):
    if p > 0:
        X *= srng.binomial(X.shape, p=1 - p)
        X /= 1 - p
    return X.astype('float32')


  def model(X, w_1, w_2, w_3, w_4, w_5, w_6, w_7, p_1, p_2):
    l1 = T.maximum(conv2d(X, w_1, border_mode='full'),0.)
    l2 = dropout(max_pool_2d(T.maximum(conv2d(l1, w_2), 0.), (2, 2)), p_1)
    l3 = dropout(max_pool_2d(T.maximum(conv2d(l2, w_3), 0.), (2, 2)), p_1)
    l4 = dropout(max_pool_2d(T.maximum(conv2d(l3, w_4), 0.), (2, 2)), p_1)
    l5 = dropout(T.flatten(max_pool_2d(T.maximum(conv2d(l4, w_5), 0.), (2, 2)), outdim=2), p_1)
    l6 = dropout(T.maximum(T.dot(l5, w_6), 0.), p_2)
    return T.nnet.softmax(T.dot(l6, w_7))

  y_hat_train = model(X, w_1, w_2, w_3, w_4, w_5, w_6, w_7, 0.2, 0.5)
  y_hat_predict = model(X, w_1, w_2, w_3, w_4, w_5, w_6, w_7, 0., 0.)
  y_x = T.argmax(y_hat_train, axis=1)

  cost = T.mean(T.nnet.categorical_crossentropy(y_hat_train, Y))


  def backprop(cost, w, alpha=0.0000000001, rho=0.9, epsilon=1e-6):
    grads = T.grad(cost=cost, wrt=w)
    updates = []
    for w1, grad in zip(w, grads):
        updates.append((w1, w1 - grad * alpha))
    return updates


  update = backprop(cost, params)

  train = theano.function(inputs=[X, Y], outputs=cost, updates=update, allow_input_downcast=True)

  y_pred = T.argmax(y_hat_predict, axis=1)
  predict = theano.function(inputs=[X], outputs=y_pred, allow_input_downcast=True)

  for i in range(num_test_data_splits):
    print predict(test_data_splits_list[i])

  miniBatchSize = 10
  def gradientDescentStochastic(epochs):
    for i in range(epochs):
        for start, end in zip(range(0, len(train_data), miniBatchSize), range(miniBatchSize, len(train_data), miniBatchSize)):
            cost = train(train_data[start:end], train_labels_b[start:end])
        
        correct_preds = 0
        for i in range(num_test_data_splits):
          correct_preds += sum(predict(test_data_splits_list[i])==test_label_splits_list[i])
        #print '\n%d) accuracy = %.4f' %(i+1, np.mean(test_labels == predict(test_data)))
        print '\n%d) accuracy = %.4f' %(i+1, (1.0*correct_preds/test_data.shape[0]))


  gradientDescentStochastic(200)


if __name__ == "__main__":
  main()


