import csv

from mrjob.job import MRJob
from mrjob.step import MRStep


class LibraryCheckoutCount(MRJob):
    '''
        Input: Records containing either checkout data or inventory data
        Output: A generated list of key/value tuples:
            Key: A book title and year, joined by a "|" character
            Value: The number of times that book was checked out in the given year
    '''

    def mapper1(self, key, val):
        '''
        reader = csv.reader(val, delimiter=',', quotechar='"')
        for line in reader:
            data = line
            print(data)
        '''
        data = val.split(',')

        # Bypass the first line containing the name of each columns
        if data[0].isdigit():
            # Inventory
            if len(data) > 6:
                bibnum, title = data[0], data[1]
                #print(bibnum, ' ', title)
                yield (bibnum, title)

            # Checkout
            else:
                bibnumber, date = data[0], data[5].split()[0]
                year = date.split('/')[2]
                #print (bibnumber, ' ', year)
                yield (bibnumber, year)

    def reducer1(self, key, vals):
        title = None
        checkout = {}

        for val in vals:
            if val.isdigit():
                checkout[val] = checkout[val]+1 if val in checkout else 1
            else:
                title = val

        if title is not None:
            for year, times in checkout.items():
                for _ in range(times):
                    yield (title, year)

    def mapper2(self, key, val):
        yield (key+'|'+val, 1)

    def reducer2(self, key, vals):
        total_sum = 0
        for val in vals:
            total_sum += 1

        yield (key, total_sum)

    def steps(self):
        return [
            MRStep(mapper=self.mapper1, reducer=self.reducer1),
            MRStep(mapper=self.mapper2, reducer=self.reducer2)
        ]


if __name__ == '__main__':
    LibraryCheckoutCount.run()
