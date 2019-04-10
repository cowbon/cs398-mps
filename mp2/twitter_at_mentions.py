from mrjob.job import MRJob
import re

WORD_REGEX = re.compile('@[A-Za-z0-9_]+')


class TwitterAtMentions(MRJob):
    '''
        Input: List of lines containing tab-separated tweets with following format:
            POST_DATETIME <tab> TWITTER_USER_URL <tab> TWEET_TEXT

        Output: A generated list of key/value tuples:
            Key: Twitter user handle (including '@' prefix)
            Value: Number of @-mentions received
    '''

    def mapper(self, key, val):
        mentioned = []

        for user in WORD_REGEX.findall(val):
            if len(user) > 3 and len(user) < 17:
                if user not in mentioned:
                    yield (user, 1)
                    mentioned.append(user)

    def reducer(self, key, vals):
        total_sum = 0

        for val in vals:
            total_sum += 1

        yield (key, total_sum)

if __name__ == '__main__':
    TwitterAtMentions.run()
