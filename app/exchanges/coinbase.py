from urls import COINBASE_PRICE_URL, COINBASE_ASSETS_URL, COINBASE_TRADES_URL
from .exchange_interface import ExchangeInterface
from .utils import make_request as request_helper, structure_coinbase
from app.supported_cryptos import NAMES
from logger.app_logger import logger
from typing import List, Dict, Any


class Coinbase(ExchangeInterface):
    __price_url = COINBASE_PRICE_URL
    __assets_url = COINBASE_ASSETS_URL
    __trades_url = COINBASE_TRADES_URL
    __assets = {}

    def __init__(self, crypto_pair: str) -> None:
        """
        Initializes a Coinbase instance.

        :param crypto_pair: The crypto pair.
        :type crypto_pair: str
        """
        self.crypto_pair = crypto_pair

    @classmethod
    async def get_assets(cls) -> Dict[str, str]:
        """
        Retrieves the assets from Coinbase.

        :raises Exception: If an error occurs while fetching the assets.

        :return: The assets dictionary.
        :rtype: Dict[str, str]
        """
        if not cls.__assets:
            try:
                response = await request_helper(cls.__assets_url)
            except Exception:
                logger.exception(f"Error while fetching assets from {cls.__assets_url}")
                raise Exception(f"Error while fetching assets from {cls.__assets_url}")
            assets = {}
            for asset in response:
                if asset["base_currency"] in NAMES and asset["quote_currency"] == "USD":
                    assets[asset["base_currency"]] = asset["id"]
            cls.__assets = assets
        return cls.__assets

    async def get_trades(self, limit: int) -> List[Dict[str, Any]]:
        """
        Retrieve trades from Coinbase exchange.

        :param limit: The maximum number of trades to retrieve.
        :type limit: int
        :return: A list of structured trades.
        :rtype: List[Dict[str, Any]]
        """
        complete_url = Coinbase.__trades_url.format(
            Coinbase.__assets[self.crypto_pair], limit
        )
        response = await request_helper(complete_url)
        structured_response = structure_coinbase(response)
        return structured_response

    async def get_bid_price(self) -> List[Dict[str, float]]:
        """
        Retrieves the bid prices from Coinbase.

        :return: The bid prices.
        :rtype: List[Dict[str, float]]
        """
        complete_url = Coinbase.__price_url.format(Coinbase.__assets[self.crypto_pair])
        response = await request_helper(complete_url)
        response = [
            {"price": float(bid[0]), "amount": float(bid[1])}
            for bid in response["bids"]
        ]
        return response

    async def get_ask_price(self) -> List[Dict[str, float]]:
        """
        Retrieves the ask prices from Coinbase.

        :return: The ask prices.
        :rtype: List[Dict[str, float]]
        """
        complete_url = Coinbase.__price_url.format(Coinbase.__assets[self.crypto_pair])
        response = await request_helper(complete_url)
        response = [
            {"price": float(ask[0]), "amount": float(ask[1])}
            for ask in response["asks"]
        ]
        return response
