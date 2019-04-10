from pyspark.mllib.feature import HashingTF, IDF
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import NaiveBayes
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
import argparse


def amazon_classification(sc, filename):
	'''
    Args:
        sc: The Spark Context
        filename: Filename of the Amazon reviews file to use, where each line represents a review
	'''

	def getData(x):
		for row in csv.reader(x, quotechar='"', escapechar='"'):
			return row
     
	def get_labeled_review(x):
		return x[6], x[9]

	def format_prediction(x):
		return "actual: {0}, predicted: {1}".format(x[0], float(x[1]))


	def produce_tfidf(x):
		tf = HashingTF().transform(x)
		idf = IDF(minDocFreq=5).fit(tf)
		tfidf = idf.transform(tf)
		return tfidf

	# Load in review
	# Parse to json
	json_payloads = SQLContext(sc).read.csv(filename, header=True, inferSchema=True, quote='"', escape='"').rdd
	data = json_payloads.map(get_labeled_review)#reviews.map(csv.reader)
	
	# Tokenize and weed out bad data
	labeled_data = (data.filter(lambda x: x[0] is not None and x[1] is not None)
								 .map(lambda x: (int(x[0]), x[1]))
								 .mapValues(lambda x: x.split()))

	labels = labeled_data.keys()

	tfidf = produce_tfidf(labeled_data.map(lambda x: x[1]))
	labeled_points = (labels.zip(tfidf)
						 .map(lambda x: LabeledPoint(x[0], x[1])))

	# Do a random split so we can test our model on non-trained data
	training, test = labeled_points.randomSplit([0.8, 0.2])

	# Train our model
	model = NaiveBayes.train(training)

	# Use our model to predict
	#train_preds = (training.map(lambda x: x.label)
	#					   .zip(model.predict(training.map(lambda x: x.features))))
	test_preds = (test.map(lambda x: x.label)
					  .zip(model.predict(test.map(lambda x: x.features))))

	# Ask PySpark for some metrics on how our model predictions performed
	#trained_metrics = MulticlassMetrics(train_preds.map(lambda x: (x[0], float(x[1]))))
	test_metrics = MulticlassMetrics(test_preds.map(lambda x: (x[0], float(x[1]))))
	#print(trained_metrics.confusionMatrix().toArray())
	#print(trained_metrics.precision())
	#print(test_metrics.confusionMatrix().toArray())
	print(test_metrics.precision())

if __name__ == '__main__':
	# Get input/output files from user
	parser = argparse.ArgumentParser()
	parser.add_argument('input', help='File to load Amazon review data from')
	args = parser.parse_args()

	# Setup Spark
	conf = SparkConf().setAppName("amazon_classification")
	sc = SparkContext(conf=conf)

	amazon_classification(sc, args.input)
