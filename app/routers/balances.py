from fastapi import APIRouter, Request
from fastapi.responses import Response

from models.schemas import Exchange
from .utils import get_balance_details
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
from slowapi.util import get_remote_address


router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/balances")
@limiter.limit("5/minute")
async def get_exchange_balance_details(request: Request, exchange: Exchange) -> dict:
    exchange = exchange.value
    if exchange == "coinbase":
        response = await get_balance_details("coinbase")
        return response
    elif exchange == "kraken":
        response = await get_balance_details("kraken")
        return response
