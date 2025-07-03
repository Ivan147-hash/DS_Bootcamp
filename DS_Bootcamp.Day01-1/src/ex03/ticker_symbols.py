import sys

def ticker_symbols():

	COMPANIES = {
		'Apple': 'AAPL',
		'Microsoft': 'MSFT',
		'Netflix': 'NFLX',
		'Tesla': 'TSLA',
		'Nokia': 'NOK'
  }

	STOCKS = {
		'AAPL': 287.73,
		'MSFT': 173.79,
		'NFLX': 416.90,
		'TSLA': 724.88,
		'NOK': 3.37
  }

	if len(sys.argv) == 2:
		INVERS_COMPANIES = {v: k for k, v in COMPANIES.items()}
		ticker = sys.argv[1].upper()
		if ticker in INVERS_COMPANIES.keys():
			print(INVERS_COMPANIES[ticker] ,STOCKS[ticker])
		else:
			print('Unknown ticker')
	else:
		sys.exit()

if __name__ == '__main__':
	ticker_symbols()