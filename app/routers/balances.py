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
    """
    Get the balance details for the specified exchange.

    :param request: The request object.
    :type request: Request
    :param exchange: The exchange value.
    :type exchange: Exchange
    :return: The balance details.
    :rtype: dict
    """
    exchange = exchange.value
    response = await get_balance_details(exchange)
    return response
