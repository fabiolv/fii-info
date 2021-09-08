from fastapi import HTTPException
from requests import api
from ..config import fii_prices_url
import requests
from datetime import datetime


def get_prices_api(ticker: str) -> dict:
    try:
        print(f'--> get_prices_api(): {fii_prices_url}/{ticker}')
        resp = requests.get(f'{fii_prices_url}/{ticker}')

        price_data = resp.json()
        print(price_data)

        if(price_data['error']):
            raise HTTPException()
    except:
        print(f'--> ERROR while retrieving the price for {ticker}')
        raise HTTPException(status_code=404, detail=f'Error while retrieving the price for {ticker}')
    
    return price_data

def get_price_value(api_data: dict) -> float:
    price = api_data['price'].replace(',', ".")
    return float(price)

def get_price_time(api_data: dict) -> str:
    '''
    Gets the time that the info was updated on the API source.
    Returns a string with the today's date and that API time
    '''
    # The raw_info is a list and the last element is the string with the time
    time = api_data['raw_info'][4]
    # "A partir de  11:13AM BRT. Mercado aberto.". We want the time...
    time = time.split()[3]
    
    date = f'{datetime.now().date()} {time}'

    return date

def get_prices_data(ticker: str) -> dict:
    try:
        price_data = {}
        price_data_api = get_prices_api(ticker)
        price_data['price'] = get_price_value(price_data_api)
        price_data['time'] = get_price_time(price_data_api)
    except HTTPException as err:
        print(f'--> ERROR while retrieving the price for {ticker}')
        raise HTTPException(status_code=404, detail=f'Error while retrieving the price for {ticker}')

    return price_data