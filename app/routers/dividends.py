from fastapi import APIRouter

router = APIRouter(tags=["Dividends"])

@router.get("/dividends/{ticker}")
def get_dividends(ticker):
    return {"ticker": ticker}