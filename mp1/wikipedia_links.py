from mrjob.job import MRJob


class WikipediaLinks(MRJob):
    '''
        Input: List of lines, each containing a user session.
            - Articles are separated by ';' characters
            - Given a session 'page_a;page_b':
                this indicates there is a link from the article page_a to page_b
            - A '<' character indicates that a user has clicked 'back' on their
                browser and has returned to the previous page they were on
        Output: The number of unique inbound links to each article
            Key: Article name (str)
            Value: Number of unique inbound links (int)
    '''

    def mapper(self, key, val):
        history = []
        words = val.split(';')
        back = 0

        for word in words:
            if word == "<":
                history.pop()
            else:
                if len(history) != 0:
                    yield (word, history[-1])

                history.append(word)

    def reducer(self, key, vals):

        # Iterate and count all occurrences of the word
        prev, count = None, 0

        for v in vals:
           if v != prev:
               count += 1
           prev = v

        # Yield the word and number of occurrences
        yield key, count


if __name__ == '__main__':
    WikipediaLinks.SORT_VALUES = True
    WikipediaLinks.run()
