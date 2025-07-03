def read_and_write():
	with open('ds.csv', 'r') as inf, open('ds.tsv', 'w') as ouf:
			for line in inf:
				result = line.replace('","', '"\t"') \
										.replace('false,', 'false\t') \
										.replace('true,', 'true\t') \
										.replace('",', '"\t')
				ouf.write(result)

if __name__ == '__main__':
	read_and_write()