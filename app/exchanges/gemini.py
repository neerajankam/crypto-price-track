from config import GEMINI_PRICE_URL, GEMINI_ASSETS_URL
from .exchange_interface import ExchangeInterface
from .utils import make_request as request_helper
from .supported_cryptos import names


class Gemini(ExchangeInterface):
    __base_url = GEMINI_PRICE_URL
    __assets_url = GEMINI_ASSETS_URL
    __assets = None

    def __init__(self, crypto_pair):
        self.crypto_pair = crypto_pair

    @classmethod
    async def get_assets(cls):
        response = await request_helper(Gemini.__assets_url)
        assets = {}
        for asset in response:
            for crypto in names:
                if crypto + "USD" == asset.upper():
                    assets[crypto] = asset.upper()
        cls.__assets = assets
        return cls.__assets

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
        complete_url = Gemini.__base_url.format(Gemini.__assets[self.crypto_pair])
        result = await request_helper(complete_url)
        return result
