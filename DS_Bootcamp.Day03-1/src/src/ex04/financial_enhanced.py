import sys
import httpx
import cProfile
import pstats
from bs4 import BeautifulSoup

def parse_financial(url, headers, value):
    try:
        response = httpx.get(url, headers=headers, follow_redirects=True)
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
                print(result)
                return
            else:
                print('Invalid name of ticker or category')
                return
    except httpx.HTTPError as e:
        raise Exception(f"Error during request to {url}: {e}")
    except Exception as e:
        raise Exception(f"Error during parsing {url}: {e}")
    
if __name__ == '__main__':
    if len(sys.argv) == 3:
        url = f'https://finance.yahoo.com/quote/{sys.argv[1]}/financials'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        value = sys.argv[2]
        # parse_financial(url, headers, value)
        filename = 'profile_financial.prof'
        profile_state = cProfile.run(f'parse_financial(url, headers, value)', filename)
        sort = pstats.Stats(filename)
        sort.sort_stats('cumulative')
        sort.print_stats(5)
    else:
        print("Invalid arguments")

# python -m cProfile -s time financial_enhanced.py 'MSFT' 'Total Revenue' > profiling-http.txt
# python -m cProfile -s ncalls financial_enhanced.py 'MSFT' 'Total Revenue' > profiling-ncalls.txt
# python3 financial_enhanced.py 'MSFT' 'Total Revenue' > pstats-cumulative.txt
