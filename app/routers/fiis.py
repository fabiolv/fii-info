from app.routers import dividends
from fastapi import APIRouter
from typing import Optional
import requests
from pydantic import BaseModel
from ..config import *

class FII(BaseModel):
    ticker: str;
    name: str;
    cnpj: str


class FIIOut(BaseModel):
    ticker: str;
    name: str;
    cnpj: str;
    period: Optional[str]
    investors: Optional[str]
    quotas: Optional[int]
    pl: Optional[float]
    vpc: Optional[float]
    profitability: Optional[float]
    fund_start: Optional[str]
    dividends_to_distribute: Optional[float]
    date_ex: Optional[str]
    payment_date: Optional[str]


router = APIRouter(tags=['FIIs'])

def get_fii_basic_info(ticker: str) -> FII:
    resp = requests.get(f"{fii_basic_url}/{ticker}")
    if resp.status_code != 200:
        return 'error'
    print(resp.json())

    data = resp.json()["data"]

    fii = FII.parse_obj(data)

    print(fii)

    return fii

@router.get("/fiis/{ticker}", response_model=FIIOut, response_model_exclude_defaults=False)
def get_ticker(ticker):
    fii = get_fii_basic_info(ticker)
    print(f"fii is {fii}")

    return fii