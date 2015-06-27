from pyspark import SparkContext
from pyspark.mllib.classification import NaiveBayes
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.regression import LabeledPoint
from PIL import Image
import numpy as np
import glob

DIRECTORY = "/root/eyes/minitrain/"
IMAGE_SIZE = 256

def main():
	"""Fits a Naive Bayes classifier to the training data"""

	sc = SparkContext(appName="Naive Bayes")

	#Opens image, resizes the image to something manageable, and converts the image to a flattened numpy array
	def make_img_array(path):
	    img = Image.open(path)
	    return np.array(img.resize((IMAGE_SIZE,IMAGE_SIZE))).ravel()

	#Create a list of tuples, image name and image path. Map the paths to array representation of the image
	image_paths = glob.glob(DIRECTORY + "*.jpeg")
	image_names = [jpeg[len(DIRECTORY):-5] for jpeg in image_paths]
	image_list = zip(image_names, image_paths)
	images = sc.parallelize(image_list).map(lambda img: (img[0], make_img_array(img[1])))

	#Import the training labels
	def make_img_labels(line):
	    parts = line.split(",")
	    return (parts[0], float(parts[1]))

	raw_labels = sc.textFile("/root/eyes/minitrain/trainLabels.csv")
	image_labels = raw_labels.map(make_img_labels)

	#Combine the images and image_labels RDDs and map them to LabeledPoints
	data = image_labels.join(images).map(lambda x: LabeledPoint(x[1][0],x[1][1]))

	#Split the  data into training and test data
	train_data, test_data = data.randomSplit( [0.8, 0.2] )
	train_data.persist()

	#Fit the model on the training data
	model = NaiveBayes.train(train_data, 1.0)

	#In-sample Performance
	train_predictions = train_data.map(lambda p : (model.predict(p.features), p.label))
	accuracy = train_predictions.filter( lambda (val, pred): val == pred ).count() / float(train_data.count())

	print "=" * 20 + "Accuracy" + "=" * 20
	print accuracy
	print "=" * 50

if __name__ == "__main__":
	main()