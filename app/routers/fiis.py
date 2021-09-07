from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
import requests
from pydantic import BaseModel
from ..config import *
from ..scrap.scrap_dividends import get_dividends_data

class FII(BaseModel):
    ticker: str
    name: str
    cnpj: str


class FIIOut(BaseModel):
    ticker: str
    name: str
    cnpj: str
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
    resp = requests.get(f"{fii_basic_url}/{ticker}")
    if resp.status_code != 200:
        raise HTTPException(404, detail="Ticker not found")

    data = resp.json()["data"]
    fii = FII.parse_obj(data)
    
    return fii

@router.get("/fiis/{ticker}", 
                response_model=FIIOut,
                # response_model_exclude_defaults=True, 
                responses={
                    200: {"model": FIIOut},
                    404: {"model": HTTPError,
                            # "description": "Ticker not found"
                        },
                } 
            )
def get_ticker(ticker):
    try:
        fii = get_fii_basic_info(ticker)
        print(f"fii is --> {fii}")
    except HTTPException:
        print(f"Ticker {ticker} not found")
        err = HTTPError(msg=f"Ticker {ticker} not found")
        print(err.json())
        return JSONResponse(status_code=404, content=err.dict())

    cnpj = fii.cnpj.replace('.', '').replace('/', '').replace('-', '')
    dividends_data = get_dividends_data(fii.ticker, cnpj, '072021')

    fii_out = FIIOut.parse_obj(fii)
    fii_out.dividends = dividends_data["dividends"]
    fii_out.date_base = dividends_data["base_date"]
    fii_out.payment_date = dividends_data["payment_date"]

    return fii_out