from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
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

class HTTPError(BaseModel):
    detail_msg: str

    class Config:
        schema_extra = {
            "example": {"detail": "The ticker was not found"},
        }

router = APIRouter(tags=['FIIs'])

def get_fii_basic_info(ticker: str) -> FII:
    resp = requests.get(f"{fii_basic_url}/{ticker}")
    if resp.status_code != 200:
        raise HTTPException(404, detail="Ticker not found")
    print(resp.json())

    data = resp.json()["data"]

    fii = FII.parse_obj(data)
    
    print(fii)

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
        return JSONResponse(status_code=404, content={"msg": f"Ticker {ticker} not found"})

    return fii