from config import GEMINI_PRICE_URL
from .exchange_interface import ExchangeInterface
from .utils import make_request as request_helper
from .mappings import crypto_mappings


MAPPINGS = crypto_mappings["gemini"]


class Gemini(ExchangeInterface):
    __base_url = GEMINI_PRICE_URL

    def __init__(self, crypto_pair):
        self.crypto_pair = crypto_pair

    async def get_bid_price(self):
        response = await self.make_request()
        response = [
            {"price": float(bid["price"]), "amount": float(bid["amount"])}
            for bid in response["bids"]
        ]
        return response

    async def get_ask_price(self):
        response = await self.make_request()
        response = [
            {"price": float(ask["price"]), "amount": float(ask["amount"])}
            for ask in response["asks"]
        ]
        return response

    async def make_request(self):
        complete_url = Gemini.__base_url.format(MAPPINGS[self.crypto_pair])
        result = await request_helper(complete_url)
        return result
