import sys

def all_stocks():

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
		string = sys.argv[1].replace(' ', '').split(",")

		for i in string:
			if not i:
				sys.exit()

		INVERS_COMPANIES = {v: k for k, v in COMPANIES.items()}
		for i in range(len(string)):
			upp_ticker = string[i].upper()
			company = string[i].title()
			if company in COMPANIES.keys():
				print(f'{company} stock price is {STOCKS[COMPANIES[company]]}')
			elif upp_ticker in INVERS_COMPANIES.keys():
				print(f'{upp_ticker} is a ticker symbol for {INVERS_COMPANIES[upp_ticker]}')
			else:
				print(string[i], 'is an unknown company or an unknown ticker symbol')
	else:
		sys.exit()

if __name__ == '__main__':
	all_stocks()