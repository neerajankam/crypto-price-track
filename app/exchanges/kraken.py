from config import KRAKEN_PRICE_URL, KRAKEN_ASSETS_URL
from .exchange_interface import ExchangeInterface
from .utils import make_request as request_helper
from .supported_cryptos import names


class Kraken(ExchangeInterface):
    __base_url = KRAKEN_PRICE_URL
    __assets_url = KRAKEN_ASSETS_URL
    __assets = None

    def __init__(self, crypto_pair):
        self.crypto_pair = crypto_pair

    @classmethod
    async def get_assets(cls):
        response = await request_helper(Kraken.__assets_url)
        response = response["result"]
        assets = {}
        for crypto in names:
            for asset in response.values():
                if asset["altname"] == crypto + "USD":
                    assets[crypto] = crypto + "USD"
        assets["BTC"] = "XXBTZUSD"
        assets["ETH"] = "XETHZUSD"
        cls.__assets = assets
        return cls.__assets

    async def get_bid_price(self):
        response = await self.make_request()
        response = [
            {"price": float(bid[0]), "amount": float(bid[1])}
            for bid in response["result"][Kraken.__assets[self.crypto_pair]]["bids"]
        ]
        return response

    async def get_ask_price(self):
        response = await self.make_request()
        response = [
            {"price": float(ask[0]), "amount": float(ask[1])}
            for ask in response["result"][Kraken.__assets[self.crypto_pair]]["asks"]
        ]
        return response

    async def make_request(self):
        complete_url = Kraken.__base_url.format(Kraken.__assets[self.crypto_pair])
        result = await request_helper(complete_url)
        return result
