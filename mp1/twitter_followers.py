from mrjob.job import MRJob
from mrjob.step import MRStep


class TwitterFollowers(MRJob):
    '''
        Input: List of follower relationships in the format "user_1 user_2",
            indicating that user_1 follows user_2 (input type is string)
        Output: A list of user pairs <user_a, user_b> such that:
                - User_a follows user_b
                - User_b follows user_a
                - User_a has at least 10 followers
                - User_b has at least 10 followers
            Output key/value tuple format:
                Key: Mutual follower pair member with lesser id (int)
                Value: Mutual follower pair member with greater id (int)
    '''
    def mapper1(self, _, val):
        key1, key2 = val.split()
        yield (int(key2), int(key1))

    def reducer1(self, key, vals):
        total_sum = 0
        data = list(vals)

        # Yield the word and number of occurrences
        if len(data) > 9:
            for val in data:
                #print(key, val)
                yield (key, val)

    def mapper2(self, key, val):
        data = []
        if val < key:
        	yield ((val, key), 1)
        else:
            yield ((key, val), 1)

    def reducer2(self, key, vals):
        total_sum = 0

        for _ in vals:
           total_sum += 1

        if total_sum > 1:
            yield (key[0], key[1])

    def steps(self):
        return [
            MRStep(mapper=self.mapper1, reducer=self.reducer1),
            MRStep(mapper=self.mapper2, reducer=self.reducer2)
        ]


if __name__ == '__main__':
    TwitterFollowers.SORT_VALUES = True
    TwitterFollowers.run()
