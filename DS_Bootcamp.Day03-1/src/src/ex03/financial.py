import sys
import requests
import time
from bs4 import BeautifulSoup

def parse_financial(url, headers, value):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        ticer = soup.find_all("div", class_='row lv-0 yf-t22klz')
        for item in ticer:
            temp = item.text
            flag = 0
            for i in range(len(value.split())):
                if value.split()[i] in temp.split():
                    flag = 1
                else:
                    flag = 0
                    break

            if flag:
                temp = temp.split()
                for i in range(len(value.split())):
                    del temp[0]
                temp.insert(0, value)
                result = tuple(temp)
                return result
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error during request to {url}: {e}")
    except Exception as e:
        raise Exception(f"Error during parsing {url}: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 3:
        url = f'https://finance.yahoo.com/quote/{sys.argv[1]}/financials'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        value = sys.argv[2]
        result = parse_financial(url, headers, value)
        if result:
            print(result)
        else:
            print("Invalid arguments")
    else:
        print("Invalid arguments")

# python3 financial.py 'AAPL' 'Total Revenue'
# python3 financial.py 'MSFT' 'Gross Profit'
