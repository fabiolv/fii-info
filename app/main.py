from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

from .config import *
from .routers import fiis, dividends, reports

app = FastAPI()

app.include_router(fiis.router)
app.include_router(dividends.router)
app.include_router(reports.router)

class FII(BaseModel):
    ticker: str

@app.get("/")
def read_root():
    print (fii_basic_url)
    return {"msg": "/docs"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None, z: Optional[str] = None):
    return {"item_id": item_id, "q": q, 'z': z}

@app.get('/ping')
def ping():
    return {'msg': 'pong'}

