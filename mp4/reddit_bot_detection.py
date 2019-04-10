from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
import argparse
import json
import sys


window_length = 300 # The size of each window "slice"
slide_interval = 10 # Interval to execute operation

def detect_reddit_bots(sc, input_dstream):
    '''
    Args:
        sc: the SparkContext
        input_dstream: The discretized stream (DStream) of input
    Returns:
        A DStream containing the list of all detected bot usernames
    '''

    # YOUR CODE HERE
    def getReddit(text):
        try:
            sub =  json.loads(text)['subreddit']
            content = json.loads(text)['text']
            author = json.loads(text)['author']
            return ((sub, author), content)
        except:
            return (None, None, None)

    def getBot(rdd):
        return len(rdd[1]) > 2

    subreddit = input_dstream.map(getReddit).groupByKeyAndWindow(window_length, slide_interval)
    res = subreddit.mapValues(list).mapValues(lambda x: len(x)).filter(lambda x: x[1] > 3)
    res.pprint()
    return res


if __name__ == '__main__':
    # Get input/output files from user
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_stream', help='Stream URL to pull data from')
    parser.add_argument('--input_stream_port', help='Stream port to pull data from')

    parser.add_argument('output', help='Directory to save DStream results to')
    args = parser.parse_args()

    # Setup Spark
    conf = SparkConf().setAppName("reddit_bot_detection")
    sc = SparkContext(conf=conf)
    ssc = StreamingContext(sc, 10)
    ssc.checkpoint('streaming_checkpoints')

    if args.input_stream and args.input_stream_port:
        dstream = ssc.socketTextStream(args.input_stream,
                                       int(args.input_stream_port))
        results = detect_reddit_bots(sc, dstream)
    else:
        print("Need input_stream and input_stream_port")
        sys.exit(1)

    results.saveAsTextFiles(args.output)
    results.pprint()

    ssc.start()
    ssc.awaitTermination()
