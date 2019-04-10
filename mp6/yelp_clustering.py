from pyspark import SparkContext, SparkConf
from pyspark.mllib.clustering import KMeans
from math import sqrt
import json
import argparse


def yelp_clustering(sc, filename):
    '''
    Args:
        sc: The Spark Context
        filename: Filename of the yelp businesses file to use, where each line represents a business
    '''

    # YOUR CODE HERE
    rdd = sc.textFile(filename)
    rdd = rdd.map(lambda x: (json.loads(x)['city'], json.loads(x)['state'], json.loads(x)['latitude'], json.loads(x)['longitude']))
    rdd = rdd.filter(lambda x: ((x[0] == 'Urbana' or x[0] == 'Champaign') and x[1] == 'IL'))
    rdd1 = rdd.map(lambda x: (x[2], x[3]))
    k = 10
    clusters = KMeans.train(rdd1, k, maxIterations=10, initializationMode="random")
    
	# Evaluate clustering by computing Within Set Sum of Squared Errors
    def error(point):
        center = clusters.centers[clusters.predict(point)]
        return sqrt(sum([x**2 for x in (point - center)]))

    WSSSE = rdd1.map(lambda point: error(point))
    print(WSSSE.collect())
    WSSSE.saveAsTextFile(str(k)+'_result.txt')
    WSSSE = rdd1.reduce(lambda x, y: x+y)
    print(str(WSSSE))
    print(str(WSSSE))
    print("Within Set Sum of Squared Error = " + str(WSSSE))

if __name__ == '__main__':
    # Get input/output files from user
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='File to load Yelp business data from')
    args = parser.parse_args()

    # Setup Spark
    conf = SparkConf().setAppName("yelp_clustering")
    sc = SparkContext(conf=conf)

    yelp_clustering(sc, args.input)
