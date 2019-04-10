from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
import argparse
import sys
import json
import re

WORD_REGEX = re.compile('#[\w]+')
window_length = 60 # The size of each window "slice"
slide_interval = 10 # Interval to execute operation


def find_trending_hashtags(sc, input_dstream):
    '''
    Args:
        sc: the SparkContext
        input_dstream: The discretized stream (DStream) of input
    Returns:
        A DStream containing the top 10 trending hashtags, and their usage count
    '''

    # YOUR CODE HERE
    def get_hashtag(text):
        try:
            data = json.loads(text)
            return WORD_REGEX.findall(data['text'])
        except:
            return []

    def get_top10(rdd):
        res = rdd.sortBy(lambda x: x[1], ascending=False).take(10)
        return rdd.filter(lambda x: x in res).sortBy(lambda x: x[1], ascending=False)

    tag_counts = input_dstream.flatMap(get_hashtag).map(lambda x: (x, 1))
    tag_count = tag_counts.reduceByKeyAndWindow(lambda x, y: x + y, None,window_length, slide_interval)
    tag_count = tag_count.transform(get_top10)
    tag_count.pprint()
    print(type(tag_count))
    return tag_count


if __name__ == '__main__':
    # Get input/output files from user
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_stream', help='Stream URL to pull data from')
    parser.add_argument('--input_stream_port', help='Stream port to pull data from')

    parser.add_argument('output', help='Directory to save DStream results to')
    args = parser.parse_args()

    # Setup Spark
    conf = SparkConf().setAppName("trending_hashtags")
    sc = SparkContext(conf=conf)
    ssc = StreamingContext(sc, 10)
    ssc.checkpoint('streaming_checkpoints')

    if args.input_stream and args.input_stream_port:
        dstream = ssc.socketTextStream(args.input_stream,
                                       int(args.input_stream_port))
        results = find_trending_hashtags(sc, dstream)
    else:
        print("Need input_stream and input_stream_port")
        sys.exit(1)

    results.saveAsTextFiles(args.output)
    results.pprint()

    ssc.start()
    ssc.awaitTermination()
