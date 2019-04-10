from pyspark import SparkContext, SparkConf
import argparse
import json


def find_engaging_reviews(sc, reviews_filename):
    '''
    Args:
        sc: The Spark Context
        reviews_filename: Filename of the Yelp reviews JSON file to use, where each line represents a review
    Returns:
        An RDD of tuples in the following format:
            (BUSINESS_ID, REVIEW_ID)
            - BUSINESS_ID: The business being referenced
            - REVIEW_ID: The ID of the review with the largest sum of "useful", "funny", and "cool" responses
                for the given business
    '''

    # YOUR CODE HERE
    def getData(x):
        data = json.loads(x)
        return (data['review_id']+' '+ str(int(data['useful'])+int(data['funny'])+int(data['cool'])))

    def getMax(x, y):
        #print(x, ' ', y)
        param1, param2 = x.split(), y.split()
        #print(param1, ' ', param2)
        if (param1[1] == param2[1]):
            return y if param1[0] < param2[0] else x
        else:
            return y if int(param1[1]) < int(param2[1]) else x

    textfile = sc.textFile(reviews_filename)
    rdd = textfile.map(lambda x: (json.loads(x)['business_id'], getData(x)))
    res = rdd.reduceByKey(getMax).mapValues(lambda v: v.split()[0])
    return res

if __name__ == '__main__':
    # Get input/output files from user
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='File to load Yelp review data from')
    parser.add_argument('output', help='File to save RDD to')
    args = parser.parse_args()

    # Setup Spark
    conf = SparkConf().setAppName("engaging_reviews")
    sc = SparkContext(conf=conf)

    results = find_engaging_reviews(sc, args.input)
    results.saveAsTextFile(args.output)

