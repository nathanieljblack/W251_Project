from PIL import Image
import numpy as np
import glob
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
import csv

DIRECTORY = "/root/train/"
IMAGE_SIZE = 256

def main():
	"""Fits a Naive Bayes classifier to the training data"""

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

	raw_labels = []
	with open("/root/train/trainLabels.csv", "rb") as f:
		reader = csv.reader(f)
		for row in reader:
			raw_labels.append(row)

	x = sorted(images)
	x = map(lambda i: i[1],x)
	x = np.array(x)
	
	y = sorted(raw_labels)
	y = map(lambda i: i[1], y)
	y = np.array(y)


	nb = MultinomialNB()
	nb.fit(x,y)

	pred = nb.predict(x)
	print classification_report(y, pred)


if __name__ == "__main__":
	main()