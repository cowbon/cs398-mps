from mrjob.job import MRJob
import re

WORD_REGEX = re.compile(r"[\w']+")


class BigramCount(MRJob):
	def mapper(self, _, val):
		prev = None
		for word in WORD_REGEX.findall(val):
			if prev is not None:
				yield (prev+','+ word, 1)

			prev = word


	def reducer(self, key, vals):
		total_sum = 0

		# Iterate and count all occurrences of the word
		for _ in vals:
			total_sum += 1

		# Yield the word and number of occurrences
		yield key, total_sum

if __name__ == '__main__':
	BigramCount.SORT_VALUES = True
	BigramCount.run()
