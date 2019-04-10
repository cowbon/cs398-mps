from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
import argparse
import sys
import json


stopwords_str = 'i,me,my,myself,we,our,ours,ourselves,you,your,yours,yourself,yourselves,he,him,his,himself,she,her,hers,herself,it,its,itself,they,them,their,theirs,themselves,what,which,who,whom,this,that,these,those,am,is,are,was,were,be,been,being,have,has,had,having,do,does,did,doing,a,an,the,and,but,if,or,because,as,until,while,of,at,by,for,with,about,against,between,into,through,during,before,after,above,below,to,from,up,down,in,out,on,off,over,under,again,further,then,once,here,there,when,where,why,how,all,any,both,each,few,more,most,other,some,such,no,nor,not,only,own,same,so,than,too,very,s,t,can,will,just,don,should,now,d,ll,m,o,re,ve,y,ain,aren,couldn,didn,doesn,hadn,hasn,haven,isn,ma,mightn,mustn,needn,shan,shouldn,wasn,weren,won,wouldn,dont,cant'
stopwords = set(stopwords_str.split(','))

window_length = 900 # The size of each window "slice"
slide_interval = 10 # Interval to execute operation


def find_subreddit_topics(sc, input_dstream):
    '''
    Args:
        sc: the SparkContext
        input_dstream: The discretized stream (DStream) of input
    Returns:
        A DStream containing the list of common subreddit words
    '''

    # YOUR CODE HERE
    def getReddit(text):
        try:
            sub =  json.loads(text)['subreddit']
            content = json.loads(text)['text'].lower().split()
            return (sub, content)
        except:
            return (None, [])

    def getTop10(entry):
        res = sorted(entry[1], key=lambda x: x[1], reverse=True)
        return (entry[0], [i[0] for i in res[:10]])

    subreddit = input_dstream.map(getReddit).flatMapValues(lambda x: x)
    #subreddit.pprint()
    filtered = subreddit.filter(lambda x: x[1] not in stopwords)
    #filtered.pprint()
    filtered = filtered.map(lambda x: (x, 1))
    word_count = filtered.reduceByKeyAndWindow(lambda x, y: x + y, None, window_length, slide_interval)
    word_count = word_count.map(lambda x: (x[0][0], (x[0][1], x[1])))
    res = word_count.groupByKeyAndWindow(window_length, slide_interval).mapValues(list)
    #res.pprint()
    res = res.map(getTop10)
    #res.pprint()
    return res


if __name__ == '__main__':
    # Get input/output files from user
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_stream', help='Stream URL to pull data from')
    parser.add_argument('--input_stream_port', help='Stream port to pull data from')

    parser.add_argument('output', help='Directory to save DStream results to')
    args = parser.parse_args()

    # Setup Spark
    conf = SparkConf().setAppName("subreddit_topics")
    sc = SparkContext(conf=conf)
    ssc = StreamingContext(sc, 10)
    ssc.checkpoint('streaming_checkpoints')

    if args.input_stream and args.input_stream_port:
        dstream = ssc.socketTextStream(args.input_stream,
                                       int(args.input_stream_port))
        results = find_subreddit_topics(sc, dstream)
    else:
        print("Need input_stream and input_stream_port")
        sys.exit(1)

    results.saveAsTextFiles(args.output)
    results.pprint()

    ssc.start()
    ssc.awaitTermination()
