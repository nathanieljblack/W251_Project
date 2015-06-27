from PIL import Image
import numpy as np
import glob
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
import csv

DIRECTORY = "/root/minitrain/"
IMAGE_SIZE = 256

def main():
	"""Fits a Naive Bayes classifier to the training data"""

	#sc = SparkContext(appName="Naive Bayes")

	#Opens image, resizes the image to something manageable, and converts the image to a flattened numpy array
	def make_img_array(path):
	    img = Image.open(path)
	    return np.array(img.resize((IMAGE_SIZE,IMAGE_SIZE))).ravel()

	#Create a list of tuples, image name and image path. Map the paths to array representation of the image
	image_paths = glob.glob(DIRECTORY + "*.jpeg")
	image_names = [jpeg[len(DIRECTORY):-5] for jpeg in image_paths]
	image_list = zip(image_names, image_paths)
	images = map(lambda img: (img[0], make_img_array(img[1])), image_list)


	#Import the training labels
	def make_img_labels(line):
	    parts = line.split(",")
	    return (parts[0], float(parts[1]))

	#raw_labels = sc.textFile("/root/minitrain/trainLabels.csv")
	#raw_labels = np.genfromtxt("/root/minitrain/trainLabels.csv", delimiter=',')
	raw_labels = []
	with open("/root/minitrain/trainLabels.csv", "rb") as f:
		reader = csv.reader(f)
		for row in reader:
			raw_labels.append(row)

	x = sorted(images)
	x = map(lambda i: i[1], x)
	x = np.array(x)
	y = sorted(raw_labels)
	y = map(lambda i: i[1], y)
	y = np.array(y)

	#image_labels = map(make_img_labels, raw_labels)

	#Combine the images and image_labels RDDs and map them to LabeledPoints
	#data = image_labels.join(images).map(lambda x: LabeledPoint(x[1][0],x[1][1]))

	#images = sorted(images)
	#image_labels = sorted(image_labels)
	nb = MultinomialNB()
	nb.fit(x,y)

	pred = nb.predict(x)
	print classification_report(y, pred)

	#Split the  data into training and test data
	#train_data, test_data = data.randomSplit( [0.8, 0.2] )
	#train_data.persist()

	#Fit the model on the training data
	#model = NaiveBayes.train(train_data, 1.0)

	#In-sample Performance
	# train_predictions = train_data.map(lambda p : (model.predict(p.features), p.label))
	# accuracy = train_predictions.filter( lambda (val, pred): val == pred ).count() / float(train_data.count())

	# print "=" * 20 + "Accuracy" + "=" * 20
	# print accuracy
	# print "=" * 50

if __name__ == "__main__":
	main()