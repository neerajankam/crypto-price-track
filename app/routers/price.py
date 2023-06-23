from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
import requests

from models.schemas import Crypto
from .utils import get_buying_selling_prices, FetchAssetsError, FetchPricesError
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address


router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/prices/{crypto}")
@limiter.limit("5/minute")
async def get_prices(request: Request, crypto: Crypto, quantity: str) -> dict:
    """
    Retrieves the buying and selling prices for a given cryptocurrency.
    Rate limit is 5 requests per minute
    :param crypto: The cryptocurrency.
    :type crypto: Crypto
    :param quantity: The quantity of the cryptocurrency.
    :type quantity: str
    :return: A dictionary containing the crypto, quantity, buying price, and selling price
    if no error is encountered. Else it returns the error message and 500 status code.
    :rtype: dict
    """
    try:
        buying_price, selling_price = await get_buying_selling_prices(crypto, quantity)
    except FetchAssetsError as e:
        return Response(content=str(e), status_code=500)
    except FetchPricesError as e:
        return Response(content=str(e), status_code=500)
    return {
        "Crypto": crypto,
        "Quantity": quantity,
        "Buying price": buying_price,
        "Selling price": selling_price,
    }
