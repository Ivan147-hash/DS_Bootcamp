from financial import parse_financial
import pytest
import requests

def test_total_revenue():
    ticer = 'MSFT'
    url = f'https://finance.yahoo.com/quote/{ticer}/financials'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    value = 'Total Revenue'
    result = parse_financial(url, headers, value)
    assert result[0] == 'Total Revenue'

def test_tuple():
    ticer = 'MSFT'
    url = f'https://finance.yahoo.com/quote/{ticer}/financials'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    value = 'Total Revenue'
    result = parse_financial(url, headers, value)
    assert type(result) == tuple

def test_error_1():
    with pytest.raises(Exception):
        ticer = ';lP'
        url = f'https://finance.yahoo.com/quote/{ticer}/financials'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        value = 'Total Revenue'
        parse_financial(url, headers, value)

# pytest
