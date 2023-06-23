from urls import KRAKEN_PRICE_URL, KRAKEN_ASSETS_URL
from .exchange_interface import ExchangeInterface
from .utils import make_request as request_helper
from app.supported_cryptos import NAMES
from logger.app_logger import logger
from typing import List, Dict, Any


class Kraken(ExchangeInterface):
    __base_url = KRAKEN_PRICE_URL
    __assets_url = KRAKEN_ASSETS_URL
    __assets = None

    def __init__(self, crypto_pair: str) -> None:
        """
        Initializes a Kraken instance.

        :param crypto_pair: The crypto pair.
        :type crypto_pair: str
        """
        self.crypto_pair = crypto_pair

    @classmethod
    async def get_assets(cls) -> Dict[str, str]:
        """
        Retrieves the assets from Kraken.

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
            response = response["result"]
            assets = {}
            for crypto in NAMES:
                for asset in response.values():
                    if asset["altname"] == crypto + "USD":
                        assets[crypto] = crypto + "USD"
            assets["BTC"] = "XXBTZUSD"
            assets["ETH"] = "XETHZUSD"
            cls.__assets = assets
        return cls.__assets

    async def get_bid_price(self) -> List[Dict[str, float]]:
        """
        Retrieves the bid prices from Kraken.

        :return: The bid prices.
        :rtype: List[Dict[str, float]]
        """
        response = await self.make_request()
        response = [
            {"price": float(bid[0]), "amount": float(bid[1])}
            for bid in response["result"][Kraken.__assets[self.crypto_pair]]["bids"]
        ]
        return response

    async def get_ask_price(self) -> List[Dict[str, float]]:
        """
        Retrieves the ask prices from Kraken.

        :return: The ask prices.
        :rtype: List[Dict[str, float]]
        """
        response = await self.make_request()
        response = [
            {"price": float(ask[0]), "amount": float(ask[1])}
            for ask in response["result"][Kraken.__assets[self.crypto_pair]]["asks"]
        ]
        return response

    async def make_request(self) -> Dict[str, Any]:
        """
        Makes a request to Kraken to retrieve data.

        :raises Exception: If an error occurs while making the request.

        :return: The response data.
        :rtype: Dict[str, Any]
        """
        complete_url = Kraken.__base_url.format(Kraken.__assets[self.crypto_pair])
        try:
            response = await request_helper(complete_url)
            return response
        except Exception:
            logger.exception(f"Error while making request to {complete_url}")
            raise Exception(f"Error while making request to {complete_url}")
