from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
import requests
from pydantic import BaseModel
from ..config import *
from ..scrape.scrape_dividends import get_dividends_data

class FII(BaseModel):
    ticker: str
    name: str
    cnpj: str


class FIIOut(BaseModel):
    ticker: str
    name: str
    cnpj: str
    price: Optional[float]
    period: Optional[str]
    investors: Optional[str]
    quotas: Optional[int]
    pl: Optional[float]
    vpc: Optional[float]
    profitability: Optional[float]
    fund_start: Optional[str]
    dividends_to_distribute: Optional[float]
    dividends: Optional[float]
    date_base: Optional[str]
    payment_date: Optional[str]

class HTTPError(BaseModel):
    msg: str

    class Config:
        schema_extra = {
            "example": {"detail": "The ticker was not found"},
        }

router = APIRouter(tags=['FIIs'])

def get_fii_basic_info(ticker: str) -> FII:
    resp = requests.get(f'{fii_basic_url}/{ticker}')
    if resp.status_code != 200:
        raise HTTPException(404, detail=f'Ticker {ticker} not found')

    data = resp.json()['data']
    fii = FII.parse_obj(data)
    
    return fii

def validate_period(period: str) -> str:
    '''
    Validates if the PERIOD passed as a URL query string is valid
    If None returns is given, returns the current MMYYYY
    Otherwise, raises an exception
    '''
    print(f'--> Validating period {period}')

    if(period is None):
        month = str(datetime.now().month).zfill(2)
        year = str(datetime.now().year)
        return f'{month}{year}'

    if(not period.isdecimal() or len(period) != 6):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f'Invalid period provided, {period}. It must be in the MMYYYY format')

    return period

@router.get("/fiis/{ticker}", 
                response_model=FIIOut,
                response_model_exclude_defaults=False, 
                responses={
                    200: {"model": FIIOut},
                    404: {"model": HTTPError,
                            # "description": "Ticker not found"
                        },
                } 
            )
def get_ticker(ticker, period: Optional[str] = None):
    try:
        period = validate_period(period)
    except HTTPException as err:
        http_error = HTTPError(msg=err.detail)
        return JSONResponse(status_code=err.status_code, content=http_error.dict())

    try:
        fii = get_fii_basic_info(ticker)
        print(f"fii is --> {fii}")
    except HTTPException as err:
        print(f'--> ERROR: Ticker {ticker} not found')
        http_error = HTTPError(msg=err.detail)
        return JSONResponse(status_code=err.status_code, content=http_error.dict())

    try:
        cnpj = fii.cnpj.replace('.', '').replace('/', '').replace('-', '')
        dividends_data = get_dividends_data(fii.ticker, cnpj, period)
    except HTTPException as err:
        print(f'--> ERROR: Could not retrieve the dividends data for {ticker} and period {period} from FNET API')
        http_error = HTTPError(msg=err.detail)

        return JSONResponse(status_code=err.status_code, content=http_error.dict())

    fii_out = FIIOut.parse_obj(fii)
    fii_out.dividends = dividends_data["dividends"]
    fii_out.date_base = dividends_data["base_date"]
    fii_out.payment_date = dividends_data["payment_date"]

    return fii_out