import requests
from fastapi import HTTPException
from bs4 import BeautifulSoup
from ..config import *


def get_dividends_fnet(ticker: str, cnpj: str, period: str) -> dict:
    '''
    Queries the FNET API to get the dividends report for a given CNPJ and MMYYYY period
    '''
    try: 
        print(f'--> get_dividends_fnet(): {fii_dividends_url}/{cnpj}?period={period}')
        resp = requests.get(f'{fii_dividends_url}/{cnpj}?period={period}')
        if(resp.status_code != 200):
            raise HTTPException(resp.status_code, detail=f'Could not find the Dividends report for {ticker} with the CNPJ {cnpj} for the period {period}')
    except:
            print(f'Could not find the Dividends report for {ticker} with the CNPJ {cnpj} for the period {period}')
            raise HTTPException(404, detail=f'Could not find the Dividends report for {ticker} with the CNPJ {cnpj} for the period {period}')
    
    return resp.json()

def validate_dividends_data(ticker: str, dividends_data: dict) -> str:
    '''
    Validates the data received from the FNET API. In some cases, we might have more than 1 report returned
    For example, there are months that we have dividends from the main ticker, but also the subscription ones
    Returns the HTML data from the dividends_data dict
    '''
    # There's only one record in that period
    if(dividends_data["recordsTotal"]) == 1:
        return dividends_data["data"]["docs"][0]["html"]
    
    for doc in dividends_data["data"]["docs"]:
        if(doc["html"].find(ticker) > 0):
            return doc["html"]

def get_dividend_value(table: BeautifulSoup) -> float:
    '''
    Scraps the value of the dividends from the HTML provided
    '''

    tr = table.find("td", text="Valor do provento por cota (R$)").parent
    dividend_value = tr.find("span", class_="dado-valores").string

    dividend_value = float(dividend_value.replace(',', "."))
    print(f'--> get_dividend_value(): {dividend_value}')

    return dividend_value

def get_dividend_base_date(table: BeautifulSoup) -> str:
    '''
    Extracts the base date from the HTML provided
    '''

    tr = table.find("td", text='Data-base (ultimo dia de negociacao com direito ao provento)').parent
    base_date = tr.find("span", class_="dado-valores").string
    print(f'--> get_dividend_base_date(): {base_date}')

    return base_date

def get_dividend_payment_date(table: BeautifulSoup) -> str:
    '''
    Extracts the payment date from the HTML provided
    '''

    tr = table.find('td', text='Data do pagamento').parent
    payment_date = tr.find('span', class_='dado-valores').string
    print(f'--> get_dividend_payment_date(): {payment_date}')

    return payment_date

def scrap_html_data(html:str) -> dict:
    '''
    Scraps the different values from the HTML and returns a dict
    '''
    # The HTML data needs to stripped, there's a lot of \n and empty spaces
    html = html.replace('\n', '').replace("  ", "")
    data = BeautifulSoup(html, 'html.parser')

    # The table that has the relevant information is the second one in the page
    table = data.find_all('table')[1]

    dividend_data = {}
    dividend_data['dividends'] = get_dividend_value(table)
    dividend_data['base_date'] = get_dividend_base_date(table)
    dividend_data['payment_date'] = get_dividend_payment_date(table)

    return dividend_data

def get_dividends_data(ticker: str, cnpj: str, period: str) -> dict:
    try:
        dividends_data = get_dividends_fnet(ticker, cnpj, period)
    except HTTPException as err:
        raise HTTPException(err.status_code, detail=err.detail)

    html = validate_dividends_data(ticker, dividends_data)

    data = scrap_html_data(html)

    return data