from config import COINBASE_PRICE_URL
from .exchange_interface import ExchangeInterface
from .utils import make_request as request_helper
from .mappings import crypto_mappings


MAPPINGS = crypto_mappings["coinbase"]


class Coinbase(ExchangeInterface):
    __base_url = COINBASE_PRICE_URL

    def __init__(self, crypto_pair):
        self.crypto_pair = crypto_pair

    async def get_bid_price(self):
        response = await self.make_request()
        response = [
            {"price": float(bid[0]), "amount": float(bid[1])}
            for bid in response["bids"]
        ]
        return response

    async def get_ask_price(self):
        response = await self.make_request()
        response = [
            {"price": float(ask[0]), "amount": float(ask[1])}
            for ask in response["asks"]
        ]
        return response

    async def make_request(self):
        complete_url = Coinbase.__base_url.format(MAPPINGS[self.crypto_pair])
        result = await request_helper(complete_url)
        return result
