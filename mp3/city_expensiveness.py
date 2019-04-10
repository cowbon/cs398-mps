from pyspark import SparkContext, SparkConf
import argparse
import json


def find_city_expensiveness(sc, business_filename):
    '''
    Args:
        sc: The Spark Context
        business_filename: Filename of the Yelp businesses JSON file to use, where each line represents a business
    Returns:
        An RDD of tuples in the following format:
            (CITY_STATE, AVERAGE_PRICE)
            - CITY_STATE is in the format "CITY, STATE". i.e. "Urbana, IL"
            - AVERAGE_PRICE should be a float rounded to 2 decimal places
    '''

    def getPrice(x):
        data = json.loads(x)
        if 'attributes' in data:
            attrs = data['attributes']
            if attrs is None:
                return None

            for attr in attrs:
                entries = attr.split()
                for i, entry in enumerate(entries):
                    if entry == 'RestaurantsPriceRange2:':
                        return float(entries[i+1])

        return None

    rdd = sc.textFile(business_filename)
    rdd = rdd.filter(lambda x:getPrice(x) is not None)
    rdd = rdd.map(lambda x: ("{}, {}".format(json.loads(x)['city'], json.loads(x)['state']), getPrice(x)))
    rdd1 = rdd.mapValues(lambda v: (v, 1))
    rdd1 = rdd1.reduceByKey(lambda a,b: (a[0]+b[0], a[1]+b[1]))
    result = rdd1.mapValues(lambda v: round(v[0]/v[1], 2))
    return result


if __name__ == '__main__':
    # Get input/output files from user
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='File to load Yelp business data from')
    parser.add_argument('output', help='File to save RDD to')
    args = parser.parse_args()

    # Setup Spark
    conf = SparkConf().setAppName("city_expensiveness")
    sc = SparkContext(conf=conf)

    results = find_city_expensiveness(sc, args.input)
    results.saveAsTextFile(args.output)

