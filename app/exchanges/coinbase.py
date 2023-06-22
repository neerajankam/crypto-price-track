from config import COINBASE_PRICE_URL, COINBASE_ASSETS_URL
from .exchange_interface import ExchangeInterface
from .utils import make_request as request_helper
from .supported_cryptos import names


class Coinbase(ExchangeInterface):
    __base_url = COINBASE_PRICE_URL
    __assets_url = COINBASE_ASSETS_URL
    __assets = None

    def __init__(self, crypto_pair):
        self.crypto_pair = crypto_pair

    @classmethod
    async def get_assets(cls):
        response = await request_helper(Coinbase.__assets_url)
        assets = {}
        for asset in response:
            if asset["base_currency"] in names and asset["quote_currency"] == "USD":
                assets[asset["base_currency"]] = asset["id"]
        cls.__assets = assets
        return cls.__assets

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
        complete_url = Coinbase.__base_url.format(Coinbase.__assets[self.crypto_pair])
        result = await request_helper(complete_url)
        return result
