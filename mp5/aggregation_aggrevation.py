from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
from pyspark.sql.types import *
import argparse


def setup_table(sc, sqlContext, reviews_filename):
    '''
    Args:
        sc: The Spark Context
        sqlContext: The Spark SQL context
        reviews_filename: Filename of the Amazon reviews file to use, where each line represents a review    
    Parse the reviews file and register it as a table in Spark SQL in this function
    '''
    schema = StructType([StructField('Id', IntegerType(), True),
	                     StructField('ProductId', StringType(), True),
						 StructField('UserId', StringType(), True),
                         StructField('ProfileName', StringType(), True), 
                         StructField('HelpfulnessNumerator', IntegerType(), True),
                         StructField('HelpfulnessDenominator', IntegerType(), True),
                         StructField('Score', IntegerType(), True),
                         StructField('Time', StringType(), True),
                         StructField('Summary', StringType(), True),
                         StructField('Text', StringType(), True)])

    df = sqlContext.read.csv(reviews_filename, header=True, schema=schema)
    
    sqlContext.registerDataFrameAsTable(df, 'table')

def query_1(sc, sqlContext):
    '''
    Args:
        sc: The Spark Context
        sqlContext: The Spark SQL context
        reviews_filename: Filename of the Amazon reviews file to use, where each line represents a review
    Returns:
        An int: the number of reviews written by the person with the maximum number of reviews written
    '''
    query = 'select max(mycount) from (select UserId, count(UserId) as mycount from table group by UserId)'
    return sqlContext.sql(query).collect()[0]['max(mycount)']

def query_2(sc, sqlContext):
    '''
    Args:
        sc: The Spark Context
        sqlContext: The Spark SQL context
    Returns:
        A list of strings: The product ids of the products with the top 25 highest average
            review scores of the products with more than 25 reviews,
            ordered by average product score, with ties broken by the number of reviews
    '''
    query = 'select ProductId, avg(Score) as average, count(ProductId) as num from table group by ProductId having num > 25 \
            order by average desc, num desc limit 25'
    #query = 'select ProductId from table where ProductId in ('+ subquery +')'
    return [str(i.ProductId) for i in sqlContext.sql(query).select('ProductId').collect()]

def query_3(sc, sqlContext):
    '''
    Args:
        sc: The Spark Context
        sqlContext: The Spark SQL context
    Returns:
        A list of integers: A `Ids` of the reviews with the top 25 highest ratios between `HelpfulnessNumerator`
            and `HelpfulnessDenominator`, which have `HelpfulnessDenominator` greater than 10,
            ordered by that ratio, with ties broken by `HelpfulnessDenominator`.
    '''
    query = 'select Id, HelpfulnessDenominator, HelpfulnessNumerator/HelpfulnessDenominator as ratio from table where \
				HelpfulnessDenominator > 10 order by ratio desc, HelpfulnessDenominator desc'
    #query = 'select Id from ('+ subquery +') limit 25'
    return [i.Id for i in sqlContext.sql(query).select('Id').take(25)]

if __name__ == '__main__':
    # Get input/output files from user
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='File to load Amazon review data from')
    args = parser.parse_args()

    # Setup Spark
    conf = SparkConf().setAppName("aggregation_aggrevation")
    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)

    setup_table(sc, sqlContext, args.input)

    result_1 = query_1(sc, sqlContext)
    result_2 = query_2(sc, sqlContext)
    result_3 = query_3(sc, sqlContext)

    print("-" * 15 + " OUTPUT " + "-" * 15)
    print("Query 1: {}".format(result_1))
    print("Query 2: {}".format(result_2))
    print("Query 3: {}".format(result_3))
    print("-" * 30)
