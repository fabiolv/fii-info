from fastapi import APIRouter

router = APIRouter(tags=["Reports"])

@router.get("/reports/{ticker}")
def get_reports(ticker):
    return {"ticker": ticker}