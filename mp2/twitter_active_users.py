import operator
from mrjob.job import MRJob
from mrjob.step import MRStep


class TwitterActiveUsers(MRJob):
    '''
        Input: List of lines containing tab-separated tweets with following format:
            POST_DATETIME <tab> TWITTER_USER_URL <tab> TWEET_TEXT

        Output: A generated list of key/value tuples:
            Key: Day in `YYYY-MM-DD` format
            Value: Twitter user handle of the user with the most tweets on this day
                (including '@' prefix)
    '''

    def mapper(self, _, val):
        date, user = val.split()[0], val.split()[2][19:]
        yield (date, user)

    def reducer(self, key, vals):
        tweeter, time = {}, 1

        for val in vals:
            if val not in tweeter:
               tweeter[val] = 1
            else:
               if tweeter[val] == time:
                  time += 1
               tweeter[val] += 1

        for _key, value in list(tweeter.items()):
            if value != time:
                del tweeter[_key]

        yield (key, '@'+sorted(tweeter)[0])


if __name__ == '__main__':
    TwitterActiveUsers.SORT_VALUES = True
    TwitterActiveUsers.run()
