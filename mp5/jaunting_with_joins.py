from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
import argparse

def setup_table(sc, sqlContext, users_filename, businesses_filename, reviews_filename):
    '''
    Args:
        sc: The Spark Context
        sqlContext: The Spark SQL context
        users_filename: Filename of the Yelp users file to use, where each line represents a user
        businesses_filename: Filename of the Yelp checkins file to use, where each line represents a business
        reviews_filename: Filename of the Yelp reviews file to use, where each line represents a review
    Parse the users/checkins/businesses files and register them as tables in Spark SQL in this function
    '''
    df1 = sqlContext.read.json(users_filename)
    df2 = sqlContext.read.json(businesses_filename)
    df3 = sqlContext.read.json(reviews_filename)
    sqlContext.registerDataFrameAsTable(df1, 'users')
    sqlContext.registerDataFrameAsTable(df2, 'businesses')
    sqlContext.registerDataFrameAsTable(df3, 'reviews')

def query_1(sc, sqlContext):
    '''
    Args:
        sc: The Spark Context
        sqlContext: The Spark SQL context
    Returns:
        An int: the maximum number of "funny" ratings left on a review created by someone who started "yelping" in 2012
    '''
    query = 'select max(reviews.funny) from reviews, users where users.yelping_since like \'2012-%\' and users.user_id=reviews.user_id'
    return sqlContext.sql(query).collect()[0]['max(funny)']

def query_2(sc, sqlContext):
    '''
    Args:
        sc: The Spark Context
        sqlContext: The Spark SQL context
    Returns:
        A list of strings: the user ids of anyone who has left a 1-star review, has created more than 250 reviews,
            and has left a review at a business in Champaign, IL
    '''
    query = 'select distinct user_id from users where review_count > 250'
    query2 = 'select distinct reviews.user_id from reviews, businesses where businesses.state="IL" and businesses.city="Champaign"\
              and reviews.business_id=businesses.business_id'
    query3 = 'select distinct user_id from reviews where stars = 1'
    query1 = 'select distinct reviews.user_id, reviews.stars from reviews, businesses where businesses.state="IL" and businesses.city="Champaign"\
              and reviews.business_id=businesses.business_id'
    df1 = sqlContext.sql('select user_id, review_count from users')#df1 = df1.intersect(df3)
    df2 = sqlContext.sql(query1)
    df2 = df2.join(df1, df1.user_id == df2.user_id, 'right')
    df2 = df2.filter((df2['stars']==1) &(df2['review_count']>250))
    return [i.user_id for i in df2.collect()]

if __name__ == '__main__':
    # Get input/output files from user
    parser = argparse.ArgumentParser()
    parser.add_argument('users', help='File to load Yelp user data from')
    parser.add_argument('businesses', help='File to load Yelp business data from')
    parser.add_argument('reviews', help='File to load Yelp review data from')
    args = parser.parse_args()

    # Setup Spark
    conf = SparkConf().setAppName("jaunting_with_joins")
    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)

    setup_table(sc, sqlContext, args.users, args.businesses, args.reviews)

    result_1 = query_1(sc, sqlContext)
    result_2 = query_2(sc, sqlContext)

    print("-" * 15 + " OUTPUT " + "-" * 15)
    print("Query 1: {}".format(result_1))
    print("Query 2: {}".format(result_2))
    print("-" * 30)
