from fastapi import APIRouter, Request
from fastapi.responses import Response

from models.schemas import Crypto
from .utils import (
    get_consolidated_prices,
    get_all_exchanges_trades,
    get_all_exchanges_prices,
    FetchAssetsError,
    FetchPricesError,
)
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
from slowapi.util import get_remote_address


router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/trades/{crypto}")
@limiter.limit("5/minute")
async def get_trades(request: Request, crypto: Crypto, limit: int) -> dict:
    response = {"crypto": crypto}
    trades = await get_all_exchanges_trades(crypto, limit)
    response.update(trades)
    return response
