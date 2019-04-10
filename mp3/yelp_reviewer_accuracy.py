from pyspark import SparkContext, SparkConf
import argparse
import json


def find_user_review_accuracy(sc, reviews_filename):
    '''
    Args:
        sc: The Spark Context
        reviews_filename: Filename of the Yelp reviews JSON file to use, where each line represents a review
    Returns:
        An RDD of tuples in the following format:
            (USER_ID, AVERAGE_REVIEW_OFFSET)
            - USER_ID: The ID of the user being referenced
            - AVERAGE_REVIEW_OFFSET: The average difference between a user's review and the average restaraunt rating
    '''
    
    # YOUR CODE HERE
    def checkValid(x):
        data = json.loads(x)
        return ('business_id' in data and 'user_id' in data)

    tf = sc.textFile(reviews_filename)
    tf = tf.filter(checkValid)

    # Get average rating for each business
    business = tf.map(lambda x: (json.loads(x)['business_id'], int(json.loads(x)['stars'])))
    business = business.mapValues(lambda v: (v, 1.0)).reduceByKey(lambda x, y: (x[0]+y[0], x[1]+y[1]))
    average = business.mapValues(lambda v: v[0]/v[1])

    # Get users' rating difference
    user = tf.keyBy(lambda x: json.loads(x)['business_id'])
    user = user.join(average).mapValues(lambda x: (json.loads(x[0])['user_id'], int(json.loads(x[0])['stars'])-x[1]))
    user = user.map(lambda x: x[1])

    #Sum up
    avgRate = user.mapValues(lambda v: (v, 1)).reduceByKey(lambda x, y: (x[0]+y[0], x[1]+y[1]))
    avgRate = avgRate.mapValues(lambda v: round(v[0]/v[1], 2))
    return avgRate


if __name__ == '__main__':
    # Get input/output files from user
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='File to load Yelp review data from')
    parser.add_argument('output', help='File to save RDD to')
    args = parser.parse_args()

    # Setup Spark
    conf = SparkConf().setAppName("yelp_reviewer_accuracy")
    sc = SparkContext(conf=conf)

    results = find_user_review_accuracy(sc, args.input)
    results.saveAsTextFile(args.output)

