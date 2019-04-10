from pyspark.mllib.regression import LabeledPoint, LinearRegressionWithSGD
from pyspark.mllib.feature import HashingTF, IDF
from pyspark.mllib.evaluation import RegressionMetrics
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
import argparse


def amazon_regression(sc, filename):
    '''
    Args:
        sc: The Spark Context
        filename: Filename of the Amazon reviews file to use, where each line represents a review    
    '''

    # YOUR CODE HERE
    def get_labeled_review(x):
        return x[4], x[5], x[9]

    def produce_tfidf(x):
        tf = HashingTF().transform(x)
        idf = IDF(minDocFreq=5).fit(tf)
        tfidf = idf.transform(tf)
        return tfidf

	
    json_payloads = SQLContext(sc).read.csv(filename, header=True, inferSchema=True, quote='"', escape='"').rdd
    data = json_payloads.map(get_labeled_review)#reviews.map(csv.reader)
	
	# Tokenize and weed out bad data
    labeled_data = (data.filter(lambda x: x[0] is not None and x[1] is not None)
        .map(lambda x: (0 if int(x[1]) == 0 else float(x[0])/int(x[1]), x[2]))
        .mapValues(lambda x: x.split()))

    labels = labeled_data.keys()
    tfidf = produce_tfidf(labeled_data.map(lambda x: x[1]))
    labeled_points = (labels.zip(tfidf)
            .map(lambda x: LabeledPoint(x[0], x[1])))

	# Do a random split so we can test our model on non-trained data
    training, test = labeled_points.randomSplit([0.8, 0.2])
    model = LinearRegressionWithSGD.train(training, iterations=10)
    
	# Use our model to predict
	#train_preds = (training.map(lambda x: x.label)
	#					   .zip(model.predict(training.map(lambda x: x.features))))
    test_preds = (test.map(lambda x: x.label)
                      .zip(model.predict(test.map(lambda x: x.features))))

	# Ask PySpark for some metrics on how our model predictions performed
	#trained_metrics = RegresionnMetrics(train_preds.map(lambda x: (x[0], float(x[1]))))
    test_metrics = RegressionMetrics(test_preds.map(lambda x: (x[0], float(x[1]))))
	#print(trained_metrics.confusionMatrix().toArray())
	#print(trained_metrics.precision())
    print(test_metrics.explainedVariance)
    print(test_metrics.rootMeanSquaredError)


if __name__ == '__main__':
    # Get input/output files from user
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='File to load Amazon review data from')
    args = parser.parse_args()

    # Setup Spark
    conf = SparkConf().setAppName("amazon_regression")
    sc = SparkContext(conf=conf)

    amazon_regression(sc, args.input)
