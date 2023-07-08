from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from models.schemas import Crypto, ViewType
from .utils import (
    get_consolidated_prices,
    get_all_exchanges_prices,
)
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
from slowapi.util import get_remote_address


router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/prices/{crypto}")
@limiter.limit("5/minute")
async def get_prices(
    request: Request, crypto: Crypto, quantity: int, view: ViewType
) -> dict:
    """
    Retrieves the buying and selling prices for a given cryptocurrency.
    Rate limit is 5 requests per minute
    :param crypto: The cryptocurrency.
    :type crypto: Crypto
    :param quantity: The quantity of the cryptocurrency.
    :type quantity: int
    :return: A dictionary containing the crypto, quantity, buying price, and selling price
    if no error is encountered. Else it returns the error message and 500 status code.
    :rtype: dict
    """
    if view == ViewType.consolidated:
        buying_price, selling_price = await get_consolidated_prices(crypto, quantity)
        return {
            "crypto": crypto,
            "quantity": quantity,
            "buying_price": buying_price,
            "selling_price": selling_price,
        }
    elif view == ViewType.individual:
        prices = await get_all_exchanges_prices(crypto, quantity)
        response = {
            "crypto": crypto,
            "quantity": quantity,
        }
        response.update(prices)
        return response
